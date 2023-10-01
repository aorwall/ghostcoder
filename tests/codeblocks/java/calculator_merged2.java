public class Calculator {

    public int multiply(int a, int b) {
        return a * b;
    }

    public int add(int a, int b) {
        return a + b;
    }

    public int subtract(int a, int b) {
        return a - b;
    }

    public static void main(String[] args) {
        Calculator calc = new Calculator();
        System.out.println("Multiplication of 2 and 3: " + calc.multiply(2, 3));
        System.out.println("Addition of 3 and 4: " + calc.add(3, 4));
        System.out.println("Subtraction of 10 and 4: " + calc.subtract(10, 4));
    }
}
