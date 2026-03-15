using WebEditor.PageCompiler;

namespace WebEditor 
{
    static class Program
    {
        public static void Main(string[] args)
        {            
            var builder = WebApplication.CreateBuilder(args);
            builder.Services.AddSingleton<ClientManager>();
            builder.Services.AddSingleton<PageManager>();

            // Add services to the container.
            builder.Services.AddRazorPages();
            var app = builder.Build();

            // // Configure the HTTP request pipeline.
            // if (!app.Environment.IsDevelopment())
            // {
            //     app.UseExceptionHandler("/Error");
            //     // The default HSTS value is 30 days. You may want to change this for production scenarios, see https://aka.ms/aspnetcore-hsts.
            //     app.UseHsts();
            // }

            app.UseHttpsRedirection();
            app.UseRouting();
            app.UseAuthorization();

            app.UseWebSockets(new WebSocketOptions
            {
                KeepAliveInterval = TimeSpan.FromMinutes(2)
            });

            ClientManager clientManager = app.Services.GetRequiredService<ClientManager>();
            PageManager pageManager = app.Services.GetRequiredService<PageManager>();

            app.Map("ws", clientManager.ConnectionRequestHandler);
            app.Map("download", pageManager.CompileRequestHandler);
            pageManager.AddCompiler("pdf", new PDFCompiler());
            pageManager.AddCompiler("txt", new TextCompiler());

            clientManager.NewClient += pageManager.NewClient;


            app.MapStaticAssets();
            app.MapRazorPages().WithStaticAssets();

            app.Run();
        }
    }
}
