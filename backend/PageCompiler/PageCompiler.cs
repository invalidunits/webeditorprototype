using System.Text;

namespace WebEditor.PageCompiler
{

    public abstract class CompiledPage : IDisposable
    {

        public abstract bool Available {get; }
        ~CompiledPage() => Dispose(false);
        public void Dispose() => Dispose(true);
        public abstract void Dispose(bool disposing);
        public abstract Stream CreateStream();
        public virtual string ContentType => "text/plain";
        
    }


    public interface IPageCompiler
    {

        // TODO: Change the arguments of this
        public Task<CompiledPage> Compile(StringBuilder page, CancellationToken token); 

    }
}
