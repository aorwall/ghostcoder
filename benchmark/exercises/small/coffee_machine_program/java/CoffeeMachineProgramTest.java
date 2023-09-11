import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertEquals;

public class CoffeeMachineProgramTest {
    @Test
    public void testCalculateMaxCups() {
        assertEquals(5, CoffeeMachineProgram.calculateMaxCups(90, 1000));
    }

    @Test
    public void testCalculateMaxCupsWithInsufficientBeans() {
        assertEquals(0, CoffeeMachineProgram.calculateMaxCups(10, 1000));
    }

    @Test
    public void testCalculateMaxCupsWithInsufficientWater() {
        assertEquals(0, CoffeeMachineProgram.calculateMaxCups(90, 100));
    }

    @Test
    public void testCalculateMaxCupsWithZeroBeans() {
        assertEquals(0, CoffeeMachineProgram.calculateMaxCups(0, 1000));
    }

    @Test
    public void testCalculateMaxCupsWithZeroWater() {
        assertEquals(0, CoffeeMachineProgram.calculateMaxCups(90, 0));
    }

    @Test
    public void testCalculateMaxCupsWithZeroBeansAndWater() {
        assertEquals(0, CoffeeMachineProgram.calculateMaxCups(0, 0));
    }
}