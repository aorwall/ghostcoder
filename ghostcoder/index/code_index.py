import logging
from typing import List, Optional

from llama_index import ServiceContext, StorageContext, load_index_from_storage, VectorStoreIndex, Document, \
     get_response_synthesizer
from llama_index.query_engine import RetrieverQueryEngine
from llama_index.response_synthesizers import ResponseMode
from llama_index.vector_stores.types import VectorStore, ExactMatchFilter, MetadataFilters
from pydantic import BaseModel, Field

from ghostcoder.filerepository import FileRepository
from ghostcoder.index.node_parser import CodeNodeParser


class BlockSearchHit(BaseModel):
    score: float = Field(default=0, description="The similarity score of the block.")
    type: str = Field(default=None, description="The type of the block.")
    identifier: str = Field(default=None, description="The identifier of the block.")
    content: str = Field(description="The content of the block.")


class FileSearchHit(BaseModel):
    path: str = Field(description="The path of the file.")
    content_type: str = Field(description="The type of the document.")
    blocks: List[BlockSearchHit] = Field(description="The blocks of the file.")


class CodeIndex:

    def __init__(self,
                 repository: FileRepository,
                 index_dir: str,
                 reload: bool = False,
                 limit: int = 5,
                 vector_store: Optional[VectorStore] = None):
        self.repository = repository
        self.vector_store = vector_store
        self.index_dir = index_dir
        self.limit = limit

        node_parser = CodeNodeParser.from_defaults(include_metadata=False)
        self.service_context = ServiceContext.from_defaults(node_parser=node_parser)

        docs = self._get_documents()

        if reload:
            self.initiate_index(docs)
            return

        try:
            storage_context = StorageContext.from_defaults(persist_dir=self.index_dir, vector_store=self.vector_store)
            self._index = load_index_from_storage(storage_context=storage_context, service_context=self.service_context, show_progress=True)
            logging.info("Index loaded from storage.")
            if self.index_dir:
                self.refresh(docs)
                self._index.storage_context.persist(persist_dir=self.index_dir)

        except FileNotFoundError:
            logging.info("Index not found. Creating a new one...")
            self.initiate_index(docs)

    def initiate_index(self, docs):
        logging.info(f"Creating new index with {len(docs)} documents...")
        storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        self._index = VectorStoreIndex.from_documents(documents=docs,
                                                      service_context=self.service_context,
                                                      storage_context=storage_context,
                                                      show_progress=True)
        if self.index_dir:
            self._index.storage_context.persist(persist_dir=self.index_dir)
            logging.info("New index created and persisted to storage.")

    def refresh(self, documents: List[Document]):
        docs_to_refresh = []
        for document in documents:
            existing_doc_hash = self._index._docstore.get_document_hash(document.get_doc_id())
            if existing_doc_hash != document.hash or existing_doc_hash is None:
                logging.debug(f"Found document to refresh: {document.get_doc_id()}. Existing hash: {existing_doc_hash}, new hash: {document.hash}")
                docs_to_refresh.append((existing_doc_hash, document))

        logging.info(f"Found {len(docs_to_refresh)} documents to refresh.")
        for i, (existing_doc_hash, document) in enumerate(docs_to_refresh):
            if existing_doc_hash != document.hash:
                logging.info(f"Refresh {document.get_doc_id()} ({i + 1}/{len(docs_to_refresh)})")
                self._index.update_ref_doc(document)
            elif existing_doc_hash is None:
                print(f"Insert {document.get_doc_id()} ({i + 1}/{len(docs_to_refresh)})")
                self._index.insert(document)

    def _get_documents(self):
        documents = []
        for file in self.repository.file_tree().traverse():
            if file.language in ["python", "java", "javascript", "typescript", "tsx"]:  # TODO: only supported
                data = self.repository.get_file_content(file.path)
                metadata = {
                    "path": file.path,
                    "language": file.language or "unknown",
                    "type": file.content_type or "code",
                }

                doc = Document(text=data, metadata=metadata)
                doc.id_ = str(file.path)

                documents.append(doc)
        return documents

    def search(self, query: str, content_type: str = None, limit: int = None):
        #filters = [ExactMatchFilter(key="block_type", value=str(block_type)) for block_type in block_types]
        filters = []

        if content_type:
            filters.append(ExactMatchFilter(key="type", value=content_type))

        retriever = self._index.as_retriever(similarity_top_k=limit or self.limit, filters=MetadataFilters(filters=filters))

        logging.debug(f"Searching for {query}...")
        nodes = retriever.retrieve(query)
        logging.info(f"Got {len(nodes)} hits")

        hits = {}
        for node in nodes:
            path = node.node.metadata.get("path")
            if path not in hits:
                hits[path] = FileSearchHit(path=path, content_type=node.node.metadata.get("type", ""), blocks=[])
            hits[path].blocks.append(BlockSearchHit(
                similarity_score=node.score,
                #identifier=node.node.metadata.get("identifier"),
                type=node.node.metadata.get("block_type"),
                content=node.node.get_content()
            ))

        return hits.values()

    def ask(self, query: str):
        #template = QuestionAnswerPrompt(DEFAULT_TEXT_QA_PROMPT_TMPL)
        response_synthesizer = get_response_synthesizer(
            response_mode=ResponseMode.COMPACT,
            #text_qa_template=template
        )
        retriever = self._index.as_retriever(similarity_top_k=20)

        query_engine = RetrieverQueryEngine(
            retriever=retriever,
            response_synthesizer=response_synthesizer,
         #   node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=0.7)],
        )
        #query_engine = self._index.as_query_engine()
        response = query_engine.query(query)
        return response
