import React, { useState } from 'react';

interface MyComponentProps {
  initialCount?: number;
}

const MyComponent: React.FC<MyComponentProps> = ({ initialCount = 0 }) => {
  const [count, setCount] = useState(initialCount);

  const resetCount = () => {
    setCount(initialCount);
  };

  return (
    <div>
      <p>You clicked {count} times</p>
      <button onClick={() => setCount(count + 1)}>
        Click me
      </button>
    </div>
  );
}

export default MyComponent;
