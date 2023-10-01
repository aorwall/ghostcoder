
import java.time.LocalDate;
// ... other imports ...

@Entity
public class Book {
    // ... other fields ...
    private LocalDate publicationDate;

    public Book() {
    }

    public Book(Long id, String title, String author, String publisher, String genre, int yearPublished,
                String isbn, double price, int pages, boolean inStock, String language, String coverType,
                String seriesName, int seriesNumber, String synopsis, double rating, int reviewCount,
                String format, String edition, String country, LocalDate publicationDate) {
        // ... other initializations ...
        this.publicationDate = publicationDate;
    }

    // ... other getters ...

    public LocalDate getPublicationDate() {
        return publicationDate;
    }

    // ... other setters ...

    public void setPublicationDate(LocalDate publicationDate) {
        this.publicationDate = publicationDate;
    }
}