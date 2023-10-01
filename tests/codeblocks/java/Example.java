package codeblocks.example;

import java.util.Random;

public class Example {

    int myVariable = 10;

    public Example() {
        myVariable = 20;
    }

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

    interface MathOperation {
        int operation(int a, int b);
    }

    MathOperation addition = (a, b) -> {
        return a + b;
    };

    public enum Colors {
        RED, GREEN, BLUE;
    }

    public @interface MyAnnotation {
        String value() default "";
    }

    public interface MyInterface {
        void myInterfaceMethod();
    }

    public static void main(String[] args) {
        Example example = new Example();
        example.myMethod(3);
    }
}