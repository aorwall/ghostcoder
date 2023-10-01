# Chunk 1
```java
package codeblocks.example;

import java.util.Random;

// ...
```

# Chunk 2
```java
package codeblocks.example;

// ...

public class Example {

    int myVariable = 10;

    // ...

    MathOperation addition = (a, b) -> {
        return a + b;
    };

    // ...
}
```

# Chunk 3
```java
package codeblocks.example;

// ...

public class Example {

    // ...

    public Example() {
        myVariable = 20;
    }

    // ...
}
```

# Chunk 4
```java
package codeblocks.example;

// ...

public class Example {

    // ...

    public void myMethod(int parameter) {
        myVariable = parameter;

        if (parameter > 5) {
            System.out.println("Parameter is greater than 5");
        }

        for (int i = 0; i < 10; i++) {
            System.out.println("For loop iteration: " + i);
        }

        while (parameter < 10) {
            System.out.println("While loop, parameter: " + parameter);
            parameter++;
        }

        // ...
    }

    // ...
}
```

# Chunk 5
```java
package codeblocks.example;

// ...

public class Example {

    // ...

    public void myMethod(int parameter) {

        // ...

        do {
            System.out.println("Do-while loop, parameter: " + parameter);
            parameter--;
        } while (parameter > 0);

        switch (parameter) {
            case 1:
                System.out.println("Parameter is 1");
                break;
            default:
                System.out.println("Parameter is default");
                break;
        }

        // ...
    }

    // ...
}
```

# Chunk 6
```java
package codeblocks.example;

// ...

public class Example {

    // ...

    public void myMethod(int parameter) {

        // ...

        try {
            Random random = new Random();
            if (random.nextBoolean()) {
                throw new Exception("Random exception");
            }
        } catch (Exception e) {
            System.out.println("Caught exception: " + e.getMessage());
        } finally {
            System.out.println("Finally block executed");
        }
    }

    // ...
}
```

# Chunk 7
```java
package codeblocks.example;

// ...

public class Example {

    // ...

    interface MathOperation {
        int operation(int a, int b);
    }

    // ...
}
```

# Chunk 8
```java
package codeblocks.example;

// ...

public class Example {

    // ...

    public enum Colors {
        RED, GREEN, BLUE;
    }

    // ...
}
```

# Chunk 9
```java
package codeblocks.example;

// ...

public class Example {

    // ...

    public @interface MyAnnotation {
        String value() default "";
    }

    // ...
}
```

# Chunk 10
```java
package codeblocks.example;

// ...

public class Example {

    // ...

    public interface MyInterface {
        void myInterfaceMethod();
    }

    // ...
}
```

# Chunk 11
```java
package codeblocks.example;

// ...

public class Example {

    // ...

    public static void main(String[] args) {
        Example example = new Example();
        example.myMethod(3);
    }
}
```

