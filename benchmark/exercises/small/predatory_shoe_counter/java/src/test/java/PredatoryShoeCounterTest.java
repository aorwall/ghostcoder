import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertEquals;

public class PredatoryShoeCounterTest {

    @Test
    public void testCountLostSocks_SingleAttack() {
        int[] distances = {100};
        int[] times = {500};
        int expected = 1;
        assertEquals(expected, PredatoryShoeCounter.countLostSocks(distances, times));
    }

    @Test
    public void testCountLostSocks_MultipleAttacks_SameTime() {
        int[] distances = {100, 200, 300};
        int[] times = {500, 500, 500};
        int expected = 1;
        assertEquals(expected, PredatoryShoeCounter.countLostSocks(distances, times));
    }

    @Test
    public void testCountLostSocks_MultipleAttacks_DifferentTimes() {
        int[] distances = {100, 200, 300};
        int[] times = {500, 600, 700};
        int expected = 3;
        assertEquals(expected, PredatoryShoeCounter.countLostSocks(distances, times));
    }

    @Test
    public void testCountLostSocks_LargeInput() {
        int[] distances = new int[100000];
        int[] times = new int[100000];
        for (int i = 0; i < 100000; i++) {
            distances[i] = i;
            times[i] = i;
        }
        int expected = 100000;
        assertEquals(expected, PredatoryShoeCounter.countLostSocks(distances, times));
    }

    @Test
    public void testCountLostSocks_NonNegativeIntegers() {
        int[] distances = {0, 1, 2};
        int[] times = {0, 1, 2};
        int expected = 3;
        assertEquals(expected, PredatoryShoeCounter.countLostSocks(distances, times));
    }

    @Test
    public void testCountLostSocks_TimeValuesDoNotExceedLimit() {
        int[] distances = {100, 200, 300};
        int[] times = {1000, 1000, 1000};
        int expected = 1;
        assertEquals(expected, PredatoryShoeCounter.countLostSocks(distances, times));
    }

    @Test
    public void testCountLostSocks_MultipleShoesSameAttackTime() {
        int[] distances = {100, 200, 300, 400};
        int[] times = {500, 500, 600, 600};
        int expected = 2;
        assertEquals(expected, PredatoryShoeCounter.countLostSocks(distances, times));
    }
}