using System.Diagnostics;
using System.Text;

namespace WebEditor.PageCompiler
{

    public class TextCompiler : IPageCompiler
    {
        private class TextPage : CompiledPage
        {
            StringBuilder myBuilder;
            public TextPage(StringBuilder builder)
            {
                lock (builder)
                {
                    myBuilder = new StringBuilder(builder.Length);
                    myBuilder.Append(builder);
                }
            }

            public override string ContentType => "text/plain";
            public override bool Available => true;
            public override void Dispose(bool disposing) { }

            public override Stream CreateStream() => 
                new MemoryStream(Encoding.UTF8.GetBytes(myBuilder.ToString()), false);
            
        }

        public async Task<CompiledPage> Compile(StringBuilder page, CancellationToken token) =>
            new TextPage(page);
        
    }
}
