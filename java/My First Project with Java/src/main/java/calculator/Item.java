package calculator;

public class Item {
    private String name;
    private int earnedTotal;

    public Item(String name, int earnedTotal) {
        this.name = name;
        this.earnedTotal = earnedTotal;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public int getEarnedTotal() {
        return earnedTotal;
    }

    public void setEarnedTotal(int earnedTotal) {
        this.earnedTotal = earnedTotal;
    }
}
