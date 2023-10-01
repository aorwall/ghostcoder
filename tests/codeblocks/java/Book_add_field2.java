import java.time.LocalDate;
import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.GenerationType;
import javax.persistence.Id;

@Entity
public class Book {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String title;
    private String author;
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