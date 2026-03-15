using System.Diagnostics;
using System.Text;

namespace WebEditor.PageCompiler
{

    public class PDFCompiler : IPageCompiler
    {
        private class PDFPage : CompiledPage
        {
            public PDFPage(DirectoryInfo PageDirectory)
            {
                this.PageDirectory = PageDirectory;
            }

            public FileInfo? PageFile => (from file in PageDirectory.GetFiles() 
                    where file.Name == "texput.pdf"
                    select file).FirstOrDefault();
            public DirectoryInfo PageDirectory { get; set; }

            public override string ContentType => "application/pdf";
            public override bool Available => PageFile?.Exists ?? false;
            public override void Dispose(bool disposing)
            {
                try
                {
                    if (PageDirectory.Exists) Directory.Delete(PageDirectory.FullName, true);
                }
                catch { }
            }

            public override Stream CreateStream()
            {
                FileInfo? info = PageFile;
                if (info is null) throw new InvalidOperationException("Unavailable page");
                return info.OpenRead();
            }
        }

        public async Task<CompiledPage> Compile(StringBuilder page, CancellationToken token)
        {
            token.ThrowIfCancellationRequested();
            PDFPage pdfpage = new(Directory.CreateTempSubdirectory());
            try
            {
                var psi = new ProcessStartInfo
                {
                    FileName = "pdflatex", // Example: Running the command prompt
                    Arguments = "-halt-on-error",
                    RedirectStandardInput = true,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    UseShellExecute = false, // Must be false to redirect streams
                    CreateNoWindow = true, // Prevents a new window from appearing
                    WorkingDirectory = pdfpage.PageDirectory.FullName
                };

                using (Process? process = Process.Start(psi))
                {
                    token.ThrowIfCancellationRequested();
                    if (process is null) throw new Exception("Couldn't start pdflatex");

                     // don't pause the server trying to compile
                    try { process.PriorityClass = ProcessPriorityClass.BelowNormal; } catch {}


                    process.StandardInput.WriteLine("\\documentclass[12pt]{article}");
                    process.StandardInput.WriteLine("\\begin{document}");
                    StringBuilder pageDocument;
                    lock (page)
                    {
                        pageDocument = new StringBuilder(page.Length);
                        pageDocument.Append(page);
                    }

                    pageDocument.Replace("{", "\\{")
                                .Replace("}", "\\}")
                                .Replace("%", "\\%")
                                .Replace("$", "\\$")
                                .Replace("&", "\\&")
                                .Replace("#", "\\#")
                                .Replace("_", "\\_")
                                .Replace("^", "\\^{}")
                                .Replace("\\", "\\textbackslash{}")
                                .Replace("~", "\\textasciitilde{}");

                    if (page.Length == 0)
                    {
                        pageDocument.Append("\\null{}");
                    }
                    process.StandardInput.Write(pageDocument);
                    process.StandardInput.WriteLine("\\end{document}");
                    token.ThrowIfCancellationRequested();
                    await process.WaitForExitAsync(token); 
                    if (!process.HasExited) throw new OperationCanceledException();


                    if (process.ExitCode != 0) 
                    {
                        Console.Error.WriteLine(process.StandardOutput.ReadToEnd());
                        throw new Exception("process failed");
                    }
                }

                pdfpage.PageDirectory.Refresh();
                if (!pdfpage.Available) throw new Exception("Failed to generate pdf page");
            }
            catch
            {
                pdfpage.Dispose();
                throw;
            }

            return pdfpage;
        }
    }
}
