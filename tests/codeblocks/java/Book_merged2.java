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
        this.id = id;
        this.title = title;
        this.author = author;
        this.publicationDate = publicationDate; // Added new field to constructor
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Long getId() {
        return id;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getAuthor() {
        return author;
    }

    public void setAuthor(String author) {
        this.author = author;
    }

    public LocalDate getPublicationDate() { // Added new getter
        return publicationDate;
    }

    public void setPublicationDate(LocalDate publicationDate) { // Added new setter
        this.publicationDate = publicationDate;
    }
}