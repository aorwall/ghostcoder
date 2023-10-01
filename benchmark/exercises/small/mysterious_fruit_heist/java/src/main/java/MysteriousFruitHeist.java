import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * This class is used to track and update the inventory of fruits in the gardens of Oodle.
 * The main functionality is to update the inventory based on the fruits that have disappeared.
 */

public class MysteriousFruitHeist {

    public List<String> updateInventory(List<String> inventory, List<String> disappeared) {
        Map<String, Integer> inventoryMap = new HashMap<>();
        for (String fruit : inventory) {
            inventoryMap.put(fruit, inventoryMap.getOrDefault(fruit, 0) + 1);
        }
        for (String fruit : disappeared) {
            inventoryMap.put(fruit, inventoryMap.getOrDefault(fruit, 0) - 1);
        }
        List<String> updatedInventory = new ArrayList<>();
        for (Map.Entry<String, Integer> entry : inventoryMap.entrySet()) {
            for (int i = 0; i < Math.max(entry.getValue(), 0); i++) {
                updatedInventory.add(entry.getKey());
            }
        }
        return updatedInventory;
    }
}