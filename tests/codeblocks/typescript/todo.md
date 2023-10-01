# Chunk 1
```typescript
import React, { useState } from 'react';

// ...

export default TodoApp;
```

# Chunk 2
```typescript
// ...

interface Todo {
  id: number;
  text: string;
  done: boolean;
}

// ...
```

# Chunk 3
```typescript
// ...

interface TodoProps {
  todo: Todo;
  onDelete: (id: number) => void;
  onToggle: (id: number) => void;
}

// ...
```

# Chunk 4
```typescript
// ...

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

// ...
```

# Chunk 5
```typescript
// ...

const TodoApp: React.FC = () => {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [input, setInput] = useState<string>("");

  // ...
};

// ...
```

# Chunk 6
```typescript
// ...

const TodoApp: React.FC = () => {

  // ...

  return (
    <div>
      <h1>Todo App</h1>end_block
      <div>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Add a todo..."
        />
        <button onClick={addTodo}>Add</button>
      </div>
      {todos.map(todo => (
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

// ...
```

# Chunk 7
```typescript
// ...

const TodoApp: React.FC = () => {
  // ...

  const addTodo = () => {
    const newTodo: Todo = {
      id: Date.now(),
      text: input,
      done: false,
    };

    setTodos(prevTodos => [...prevTodos, newTodo]);
    setInput("");
  };

  // ...
};

// ...
```

# Chunk 8
```typescript
// ...

const TodoApp: React.FC = () => {
  // ...

  const deleteTodo = (id: number) => {
    setTodos(prevTodos => prevTodos.filter(todo => todo.id !== id));
  };

  // ...
};

// ...
```

# Chunk 9
```typescript
// ...

const TodoApp: React.FC = () => {
  // ...

  const toggleTodo = (id: number) => {
    setTodos(prevTodos =>
      prevTodos.map(todo =>
        todo.id === id ? { ...todo, done: !todo.done } : todo
      )
    );
  };

  // ...
};

// ...
```

