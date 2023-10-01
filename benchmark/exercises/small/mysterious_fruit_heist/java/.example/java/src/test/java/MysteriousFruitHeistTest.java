import org.junit.jupiter.api.Test;
import java.util.Arrays;
import java.util.List;
import static org.junit.jupiter.api.Assertions.assertEquals;

public class MysteriousFruitHeistTest {

    MysteriousFruitHeist heist = new MysteriousFruitHeist();

    @Test
    public void testUpdateInventory() {
        List<String> inventory = Arrays.asList("apple", "banana", "cherry", "apple", "banana");
        List<String> disappeared = Arrays.asList("apple", "banana");
        List<String> expected = Arrays.asList("cherry", "apple", "banana");
        assertEquals(expected, heist.updateInventory(inventory, disappeared));
    }
}