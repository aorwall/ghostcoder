// ... other import statements ...
import java.time.LocalDate;

// ... other fields ...
private LocalDate publicationDate;

// ... other constructors ...
public Book(Long id, String title, String author, String publisher, String genre, int yearPublished,
            String isbn, double price, int pages, boolean inStock, String language, String coverType,
            String seriesName, int seriesNumber, String synopsis, double rating, int reviewCount,
            String format, String edition, String country, LocalDate publicationDate) {
    // ... other field initializations ...
    this.publicationDate = publicationDate;
}

// ... other getter methods ...
public LocalDate getPublicationDate() {
    return publicationDate;
}

// ... other setter methods ...
public void setPublicationDate(LocalDate publicationDate) {
    this.publicationDate = publicationDate;
}