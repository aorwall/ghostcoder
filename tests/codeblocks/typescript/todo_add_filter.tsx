// ... (rest of the imports and types)

enum Filter {
  All = 'ALL',
  Active = 'ACTIVE',
  Completed = 'COMPLETED',
}

const TodoApp: React.FC = () => {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [input, setInput] = useState<string>("");
  const [currentFilter, setCurrentFilter] = useState<Filter>(Filter.All);

  // ... (rest of the useState logic and methods)

  const filteredTodos = () => {
    switch (currentFilter) {
      case Filter.Active:
        return todos.filter(todo => !todo.done);
      case Filter.Completed:
        return todos.filter(todo => todo.done);
      default:
        return todos;
    }
  };

  return (
    <div>
      <h1>Todo App</h1>
      <div>
        <select
          value={currentFilter}
          onChange={(e) => setCurrentFilter(e.target.value as Filter)}
        >
          <option value={Filter.All}>All</option>
          <option value={Filter.Active}>Active</option>
          <option value={Filter.Completed}>Completed</option>
        </select>
      </div>
      <div>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Add a todo..."
        />
        <button onClick={addTodo}>Add</button>
      </div>
      {filteredTodos().map(todo => (
        <TodoItem
          key={todo.id}
          todo={todo}
          onDelete={deleteTodo}
          onToggle={toggleTodo}
        />
      ))}
    </div>
  );
};

export default TodoApp;