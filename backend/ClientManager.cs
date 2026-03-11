
using System.Collections.Concurrent;
using System.Net.WebSockets;
using Microsoft.AspNetCore.Authentication;

namespace WebEditor 
{
    public class ClientManager
    {
        public event Action<Client> NewClient = delegate { };
        public async Task ConnectionRequestHandler(HttpContext context)
        {
            if (!context.WebSockets.IsWebSocketRequest) throw new InvalidOperationException();
            WebSocket socket = await context.WebSockets.AcceptWebSocketAsync();
            var client = new Client(socket);
            NewClient.Invoke(client);
            await client.RecieveData();
        }
    }
}