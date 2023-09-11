public class CoffeeMachineProgram {
    public static int calculateMaxCups(int coffeeBeans, int water) {
        int coffeeCups = coffeeBeans / 18;
        int waterCups = water / 200;
        return Math.min(coffeeCups, waterCups);
    }
}