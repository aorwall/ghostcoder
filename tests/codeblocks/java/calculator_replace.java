public class Calculator {
    public int multiply(int a, int b) {
        return a * b;
    }

    public static void main(String[] args) {
        Calculator calc = new Calculator();
        System.out.println("Multiplication of 2 and 3: " + calc.multiply(2, 3));
    }
}
