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

        private void InsertText(string text, int position)
        {
            lock (page) 
            {
                page.Insert(position, text);
                lock (clients) foreach (PageClient pc in clients)
                {
                    lock (pc)
                    {
                        if (pc.selectionBegin >= position) 
                        {
                            pc.selectionBegin += text.Length;
                            pc.selectionEnd += text.Length;
                        }
                    }
                } 
                UpdateClients();
            }

        }

        private void DeleteText(int position, int count)
        {
            lock (page) 
            {
                int startdel = position - count;
                page.Remove(startdel, count);
                lock (clients) foreach (PageClient pc in clients)
                {
                    lock (pc)
                    {
                        if (pc.selectionBegin >= startdel) 
                        {
                            pc.selectionBegin -= Math.Min(count, pc.selectionBegin-startdel);
                            pc.selectionEnd -= Math.Min(count, pc.selectionEnd-startdel);
                        }
                    }
                } 
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

        private void ReplaceSelection(int selectionBegin, int selectionEnd, string text)
        {
            lock (page) 
            {
                page.Remove(selectionBegin, selectionEnd-selectionBegin);
                page.Insert(selectionBegin, text);
                int newSelectionEnd = selectionBegin + text.Length;
                int diff = (selectionEnd - selectionBegin) - text.Length;
                lock (clients)  foreach (PageClient pc in clients)
                {
                    lock (pc)
                    {
                        if (pc.selectionBegin > selectionBegin)
                        {
                            pc.selectionBegin -= Math.Min(pc.selectionBegin - selectionBegin, diff);
                            pc.selectionEnd -= Math.Min(pc.selectionEnd - selectionBegin, diff);
                        }
                    }
                } 
                UpdateClients();
            }
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