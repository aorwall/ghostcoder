package codeblocks;

import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.util.List;
import java.util.function.Consumer;

public class TreeSitterTypes implements ExampleInterface {

    // This is a single line comment.

    private int value;

    public static String CONSTANT = "foo"

    public TreeSitterTypes(int value) {
        this.value = value;
    }

    void literalsAndExpressions() {
        int a = 4, b = 3;
        String b = "4";
        double decimal = 5.5;

        int intValue = (int) decimal;  // cast expression

        boolean bresult = (5 > 3) && (3 < 4);  // binary expression
        int hex = 0x1A;
        boolean isTrue = true;
        char charLit = 'A';
        String strLit = "Hello";
        String multiLine = """
                           Hello
                           World
                           """;
        int result = intValue < hex ? intValue : hex;
        String interpolated = String.format("Value: %d", decimal);
        String[] array = new String[]{"A", "B"};
        String letterA = array[0];
        switch (intValue) {
            case 10 -> System.out.println("Ten");
            default -> throw new IllegalStateException("Unexpected value: " + decimal);
        }
    }


    interface ExampleInterface {
        void exampleMethod();
    }

    /**
     * This is a javadoc comment.
     * @param args command-line arguments.
     */
    @Override
    public void exampleMethod() {
        System.out.println("Implementation");
    }

    public void lambda() {
        Consumer<String> lambda = s -> System.out.println(s);  // lambda expression
        lambda.accept("Hello Lambda!");

        Consumer<String> methodRef = System.out::println;  // method reference
        methodRef.accept("Hello Method Reference!");
    }

    void statementsAndControls() {
        int value = 5;
        if (value == 5) {
            System.out.println("Five");
        } else if (value == 6) {
            System.out.println("Six");
        } else {
            System.out.println("Other");
        }

        try (AutoCloseable ac = () -> {}) {
            System.out.println("In try");
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            System.out.println("In finally");
        }
    }

    void methodWithParameters(String a, int... b) {
        System.out.println(a);
        for (int val : b) {
            System.out.println(val);
        }
    }

    enum Day {
        MONDAY, TUESDAY, WEDNESDAY;
    }

    record Person(String name, int age) {}

    public static void main(String[] args) {
        new TreeSitterTypes(0).literalsAndExpressions();
    }

    public static void printList(List<?> list) {  // wildcard
        for (Object item : list) {
            System.out.println(item);
        }
    }

    public static class PatternsAndSynchronization {

        sealed interface Shape permits Circle, Square {}

        record Circle(double radius) implements Shape {}
        record Square(double side) implements Shape {}

        private final Object lock = new Object();

        public void synchronizedMethod() {
            synchronized(lock) {
                System.out.println("Inside synchronized block");
            }
        }

        public static void main(String[] args) {
            PatternsAndSynchronization obj = new PatternsAndSynchronization();
            obj.synchronizedMethod();

            Shape shape = new Circle(5.0);
            if (shape instanceof Circle c)
                System.out.println("Circle with radius: " + c.radius());

        }
    }

    public class ExampleTypesAnnotations {

        @Retention(RetentionPolicy.RUNTIME)
        @interface MyAnnotation {
            String value() default "Default Value";
        }

        @MyAnnotation(value = "Custom Value")
        class AnnotatedClass {
            private float floatValue;
        }

        public static void main(String[] args) {
            MyAnnotation annotation = AnnotatedClass.class.getAnnotation(MyAnnotation.class);
            System.out.println(annotation.value());
        }
    }
}
