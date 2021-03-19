package Tests.SampleData.SourceCode;

/**
 * Some sample class documentation
 *
 * @author ClassTestAuthor
 */
@Entity
public class Test {
    /**
     * Some sample method documentation
     *
     * @author MethodTestAuthor
     */
    public Test(int someConstructorParameter) {
        //inlineTestComment
    }

    @Id
    @GeneratedValue
    public int testMethod(int someMethodParameter) {
        return someMethodParameter;
    }
}
