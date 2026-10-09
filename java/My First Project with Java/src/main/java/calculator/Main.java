package calculator;

import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        int sum = 202 + 118 + 2250 + 1680 + 1075 + 80;
        System.out.println("""
                Earned amount:
                Bubblegum: $202
                Toffee: $118
                Ice cream: $2250
                Milk chocolate: $1680
                Doughnut: $1075
                Pancake: $80
                """);
        System.out.println("Income: " +sum);
        System.out.println("Staff expenses");
        sum-=scanner.nextInt();
        System.out.println("Other expenses");
        sum-=scanner.nextInt();
        System.out.println("Net income: " + sum);

    }

}