import React, { useState } from 'react';

interface Todo {
  id: number;
  text: string;
  done: boolean;
}

interface TodoProps {
  todo: Todo;
  onDelete: (id: number) => void;
  onToggle: (id: number) => void;
}

const TodoItem: React.FC<TodoProps> = ({ todo, onDelete, onToggle }) => {
  return (
    <div>
      <span
        style={{ textDecoration: todo.done ? 'line-through' : 'none' }}
        onClick={() => onToggle(todo.id)}
      >
        {todo.text}
      </span>
      <button onClick={() => onDelete(todo.id)}>Delete</button>
    </div>
  );
};

enum Filter {
  All = 'ALL',
  Active = 'ACTIVE',
  Completed = 'COMPLETED',
}

const TodoApp: React.FC = () => {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [input, setInput] = useState<string>("");
  const [currentFilter, setCurrentFilter] = useState<Filter>(Filter.All);

  const addTodo = () => {
    const newTodo: Todo = {
      id: Date.now(),
      text: input,
      done: false,
    };

    setTodos(prevTodos => [...prevTodos, newTodo]);
    setInput("");
  };

  const deleteTodo = (id: number) => {
    setTodos(prevTodos => prevTodos.filter(todo => todo.id !== id));
  };

  const toggleTodo = (id: number) => {
    setTodos(prevTodos =>
      prevTodos.map(todo =>
        todo.id === id ? { ...todo, done: !todo.done } : todo
      )
    );
  };

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