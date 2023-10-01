import java.util.HashSet;
import java.util.Set;

public class PredatoryShoeCounter {

    public static int countLostSocks(int[] distances, int[] times) {
        Set<Integer> uniqueAttackTimes = new HashSet<>();
        for (int time : times) {
            uniqueAttackTimes.add(time);
        }
        return uniqueAttackTimes.size();
    }
}