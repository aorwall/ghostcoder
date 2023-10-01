import java.time.LocalDate;
// ...

@Entity
public class Book {
    // ...
    private LocalDate publicationDate; // Added new field

    public Book() {
    }

    public Book(Long id, String title, String author, LocalDate publicationDate) { // Updated constructor
        // ...
        this.publicationDate = publicationDate; // Added new field to constructor
    }

    // ...

    public LocalDate getPublicationDate() { // Added new getter
        return publicationDate;
    }

    public void setPublicationDate(LocalDate publicationDate) { // Added new setter
        this.publicationDate = publicationDate;
    }
}