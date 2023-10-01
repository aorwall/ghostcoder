import org.junit.jupiter.api.Test;
import java.util.Arrays;
import java.util.ArrayList;
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

    @Test
    public void testUpdateInventoryWithNonExistingFruit() {
        List<String> inventory = Arrays.asList("apple", "banana", "cherry");
        List<String> disappeared = Arrays.asList("grape");
        List<String> expected = Arrays.asList("apple", "banana", "cherry");
        assertEquals(expected, heist.updateInventory(inventory, disappeared));
    }

    @Test
    public void testUpdateInventoryWithEmptyDisappearedList() {
        List<String> inventory = Arrays.asList("apple", "banana", "cherry");
        List<String> disappeared = new ArrayList<>();
        List<String> expected = Arrays.asList("apple", "banana", "cherry");
        assertEquals(expected, heist.updateInventory(inventory, disappeared));
    }

    @Test
    public void testUpdateInventoryWithEmptyInventory() {
        List<String> inventory = new ArrayList<>();
        List<String> disappeared = Arrays.asList("apple", "banana");
        List<String> expected = new ArrayList<>();
        assertEquals(expected, heist.updateInventory(inventory, disappeared));
    }

    @Test
    public void testUpdateInventoryWithMultipleOccurrences() {
        List<String> inventory = Arrays.asList("apple", "apple", "apple", "banana", "banana");
        List<String> disappeared = Arrays.asList("apple", "banana");
        List<String> expected = Arrays.asList("apple", "apple", "banana");
        assertEquals(expected, heist.updateInventory(inventory, disappeared));
    }
}