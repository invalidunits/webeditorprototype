using System.Collections.Concurrent;
using System.Text;
using System.Text.Json;
using Microsoft.AspNetCore.Mvc.RazorPages;
using WebEditor;
using WebEditor.Models;
namespace WebEditor 
{
    partial class PageManager
    {
        LinkedList<PageClient> clients;
        private StringBuilder page;
        public PageManager()
        {
            page = new StringBuilder();
            clients = [];
        }

        public void NewClient(Client client)
        {
            lock (clients)
            {
                clients.AddLast(new PageClient(this, client));
            }
        }


        private void InsertText(string text, int position, IEnumerable<PageClient> insertionClient)
        {
            lock (clients) 
            {
                page.Insert(position, text);
                foreach (PageClient pc in clients.Except(insertionClient)) if (pc.selectionBegin > position) pc.selectionBegin += text.Length;
                UpdateClients();
            }

        }

        private void UpdateClients()
        {
            Task.WaitAll(clients.Select(x => x.client.Socket.SendAsync(Encoding.UTF8.GetBytes(
                JsonSerializer.Serialize(new PageUpdate()
                {
                    data = page.ToString(),
                    selection = new PageAction.SelectionType{ start = x.selectionBegin, end = x.selectionEnd }
                }, new JsonSerializerOptions { IncludeFields = true })
            ), System.Net.WebSockets.WebSocketMessageType.Text, true, CancellationToken.None)).ToArray());
        }

        private void RemoveClient(PageClient client)
        {
            lock (clients)
            {
                clients.Remove(client);
            }
        }        
    }
}