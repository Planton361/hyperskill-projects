package cinema;

import java.util.Scanner;

public class Cinema {

    private final int[][] cinemaSeat;
    private final boolean isBig;
    private int numberOfPurchasedTickets;
    private double percentage;
    private int currentIncome;
    private int totalIncome;

    Cinema(int[][] cinemaSeat, boolean isBig) {
        this.cinemaSeat = cinemaSeat;
        this.isBig = isBig;
        calculateTotalIncome();
    }

    private void calculateTotalIncome() {
        totalIncome = 0;
        for(int i = 0; i < cinemaSeat.length; i++){
            for(int j = 0; j < cinemaSeat[0].length; j++){
                if(isBig && i >= cinemaSeat.length / 2)
                    totalIncome += 8;
                else
                    totalIncome += 10;
            }
        }
    }

    public static void main(String[] args) {

        Scanner scanner = new Scanner(System.in);
        Cinema cinema = initializeCinema(scanner);
        startCinema(cinema, scanner);
    }

    private static void startCinema(Cinema cinema, Scanner scanner) {
        while(true){
            printMenu();
            int choice = scanner.nextInt();
            switch(choice){
                case 1:
                    cinema.printCinema();
                    break;
                case 2:
                    cinema.buyTicket(scanner);
                    break;
                case 3:
                    cinema.statistics();
                    break;
                case 0:
                    return;
            }
        }
    }

    private void statistics() {
        System.out.println("Number of purchased tickets: " + numberOfPurchasedTickets);
        System.out.printf("Percentage: %.2f%%\n", calculatePercentage());
        System.out.println("Current income: $" + currentIncome);
        System.out.println("Total income: $" + totalIncome);
    }

    private double calculatePercentage(){
        percentage = ((double) (numberOfPurchasedTickets * 100) / (cinemaSeat.length * cinemaSeat[0].length));
        return percentage;
    }

    private static void printMenu() {
        System.out.println("""
                1. Show the seats
                2. Buy a ticket
                3. Statistics
                0. Exit
                """);
    }

    private void buyTicket(Scanner scanner) {
        int rowNumber;
        while(true){
            System.out.println("Enter a row number:");
            rowNumber = scanner.nextInt();
            System.out.println("Enter a seat number in that row:");
            int seatNumber = scanner.nextInt();
            if(rowNumber < 1 || rowNumber > cinemaSeat.length || seatNumber < 1 || seatNumber > cinemaSeat[0].length)
                System.out.println("Wrong input!");
            else if(cinemaSeat[rowNumber - 1][seatNumber - 1] == 1)
                System.out.println("That ticket has already been purchased!");
            else{
                cinemaSeat[rowNumber - 1][seatNumber - 1] = 1;
                break;
            }
        }
        int ticketPrice = !isBig || rowNumber <= cinemaSeat.length / 2 ? 10 : 8;
        System.out.println();
        System.out.println("Ticket price: $" + ticketPrice);
        numberOfPurchasedTickets++;
        currentIncome += ticketPrice;
        printCinema();
    }

    private void printCinema() {
        System.out.println();
        System.out.println("Cinema:");
        printFirstRow(cinemaSeat[0].length);
        for (int i = 0; i < cinemaSeat.length; i++) {
            System.out.print(i + 1);
            for (int j = 0; j < cinemaSeat[i].length; j++) {
                System.out.print(" " + seatStatus(i, j));
            }
            System.out.println();
        }
        System.out.println();
    }

    private String seatStatus(int i, int j) {
        return cinemaSeat[i][j] == 1 ? "B" : "S";
    }

    private void printFirstRow(int length) {
        System.out.print(" ");
        for (int i = 1; i <= length; i++) {
            System.out.print(" " + i);
        }
        System.out.println();
    }

    private static Cinema initializeCinema(Scanner scanner) {
        System.out.println("Enter the number of rows:");
        int numberOfRows = scanner.nextInt();

        System.out.println("Enter the number of seats in each row:");
        int numberOfSeats = scanner.nextInt();

        boolean isBig = numberOfSeats * numberOfRows > 60;

        return new Cinema(new int[numberOfRows][numberOfSeats], isBig);
    }
}
