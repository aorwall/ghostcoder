public class Calculator {

    public int multiply(int a, int b) {
        return a * b;
    }

    // ... (existing methods)

    public static void main(String[] args) {
        Calculator calc = new Calculator();
        System.out.println("Multiplication of 2 and 3: " + calc.multiply(2, 3));
        // ... (existing method calls)
    }
}
