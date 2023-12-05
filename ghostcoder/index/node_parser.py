import logging
import traceback
from typing import Sequence, List, Optional, Dict, Any

from langchain.text_splitter import TextSplitter, TokenTextSplitter
from llama_index import Document
from llama_index.callbacks import CBEventType, CallbackManager
from llama_index.callbacks.schema import EventPayload
from llama_index.node_parser import NodeParser
from llama_index.schema import BaseNode, MetadataMode, TextNode, NodeRelationship
from llama_index.utils import get_tqdm_iterable

from ghostcoder.codeblocks import create_parser, CodeBlock, CodeBlockType
from ghostcoder.utils import count_tokens


class CodeNodeParser(NodeParser):

    @classmethod
    def from_defaults(
        cls,
        chunk_size: int = 4000,
        include_metadata: bool = True,
        include_prev_next_rel: bool = True,
        callback_manager: Optional[CallbackManager] = None,
    ) -> "CodeNodeParser":
        callback_manager = callback_manager or CallbackManager([])

        token_text_splitter = TokenTextSplitter(
            chunk_size=chunk_size
        )
        return cls(
            text_splitter=token_text_splitter,
            include_metadata=include_metadata,
            include_prev_next_rel=include_prev_next_rel,
            callback_manager=callback_manager,
        )

    @classmethod
    def class_name(cls):
        return "CodeNodeParser"

    def _parse_nodes(
        self,
        nodes: Sequence[BaseNode],
        show_progress: bool = False,
        **kwargs: Any,
    ) -> List[BaseNode]:
        nodes_with_progress = get_tqdm_iterable(
            nodes, show_progress, "Parsing documents into nodes"
        )

        all_nodes: List[BaseNode] = []
        for node in nodes_with_progress:
            language = node.metadata.get("language", None)
            if language:
                try:
                    parser = create_parser(language)
                except Exception as e:
                    logging.warning(
                        f"Could not get parser for language {language}. Will not parse document {node.id_}")
                    continue

                content = node.get_content(metadata_mode=MetadataMode.NONE)
                if not content:
                    logging.warning(f"Could not get content for document {node.id_}")
                    continue

                codeblock = parser.parse(content)

                splitted_blocks = codeblock.split_blocks()

                for splitted_block in splitted_blocks:
                    definitions, parent = self.get_parent_and_definitions(splitted_block)

                    node_metadata = node.metadata

                    if splitted_block.type in [CodeBlockType.TEST_CASE, CodeBlockType.TEST_SUITE]:
                        node_metadata["purpose"] = "test"

                    node_metadata["block_type"] = str(splitted_block.type)

                    if splitted_block.identifier:
                        node_metadata["identifier"] = str(splitted_block.identifier)

                    tokens = count_tokens(parent.to_string())
                    if tokens > 4000:
                        logging.info(
                            f"Skip node [{splitted_block.identifier}] in {node.id_} with {tokens} tokens")
                        logging.debug(codeblock.to_tree(include_tree_sitter_type=False,
                                                        show_tokens=True,
                                                        include_types=[CodeBlockType.FUNCTION, CodeBlockType.CLASS]))

                        continue

                    if tokens > 1000:
                        logging.info(f"Big node [{splitted_block.identifier}] in {node.id_} with {tokens} tokens")
                        logging.debug(codeblock.to_tree(include_tree_sitter_type=False,
                                                        show_tokens=True,
                                                        include_types=[CodeBlockType.FUNCTION, CodeBlockType.CLASS]))

                    # TODO: Add relationships between code blocks
                    node = TextNode(
                        text=parent.to_string(),
                        embedding=node.embedding,
                        metadata=node_metadata,
                        excluded_embed_metadata_keys=node.excluded_embed_metadata_keys,
                        excluded_llm_metadata_keys=node.excluded_llm_metadata_keys,
                        metadata_seperator=node.metadata_seperator,
                        metadata_template=node.metadata_template,
                        text_template=node.text_template,
                        relationships={NodeRelationship.SOURCE: node.as_related_node_info()},
                    )

                    all_nodes.append(node)

        return all_nodes

    def get_parent_and_definitions(self, codeblock: CodeBlock) -> (List[str], CodeBlock):
        definitions = [codeblock.content]
        if codeblock.parent:
            parent_defs, parent = self.get_parent_and_definitions(codeblock.parent)
            definitions.extend(parent_defs)
            return definitions, parent
        else:
            return definitions, codeblock
