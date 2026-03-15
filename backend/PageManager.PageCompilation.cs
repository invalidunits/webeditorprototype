using System.Collections;
using WebEditor.PageCompiler;

namespace WebEditor 
{
    partial class PageManager
    {
        private class _PageCompilerCache
        {
            public PageManager manager;
            public IPageCompiler compiler;
            private Task<CompiledPage>? cachedPage;
            private Lazy<CancellationTokenSource> cachedtokenSource;

            public _PageCompilerCache(PageManager manager, IPageCompiler compiler)
            {
                this.manager = manager;
                this.compiler = compiler;
                this.cachedPage = null;
                this.cachedtokenSource = new();
            }

            public Task<CompiledPage> CompileCache(bool needsNew)
            {
                if (cachedPage is null || needsNew)
                {
                    if (cachedtokenSource.IsValueCreated)
                    {
                        cachedtokenSource.Value.Cancel();
                    }
                    
                    cachedtokenSource = new(new CancellationTokenSource());
                    cachedPage = compiler.Compile(manager.page, cachedtokenSource.Value.Token);
                }

                return cachedPage;
            }
        }
        private Dictionary<string, _PageCompilerCache> compilerCache = new();
        public void AddCompiler(string name, IPageCompiler compiler)
        {
            lock (compilerCache)
            {
                compilerCache.Add(name, new _PageCompilerCache(this, compiler));
            }
        }

        public Task<CompiledPage> Compile(string name, bool needsNew = false)
        {
            _PageCompilerCache cache;
            lock (compilerCache) cache = compilerCache[name];
            lock (cache)
            {
                return cache.CompileCache(needsNew);;
            }
        }
    }
}