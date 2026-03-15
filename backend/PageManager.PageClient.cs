using System.Net.WebSockets;
using System.Text;
using Newtonsoft.Json;
using WebEditor.Models;

namespace WebEditor 
{
    partial class PageManager
    {
        class PageClient 
        {
            public readonly PageManager manager;
            public readonly Client client;
            public bool IsClosed => !client.Recieving;
            public int selectionBegin;
            public int selectionEnd;

            public PageClient(PageManager manager, Client client)
            {
                this.manager = manager;
                this.client = client;
                selectionBegin = 0;
                selectionEnd = 0;

                this.client.Parse += ParseData;
                this.client.Closed += Closed;
            }


            private void ParseData(WebSocketReceiveResult result, ReadOnlySpan<byte> data)
            {
                lock (this)
                {
                    string text = Encoding.UTF8.GetString(data);
                    var action = JsonConvert.DeserializeObject<PageAction>(text);
                    switch (action.Type)
                    {
                        case PageAction.ActionType.Select:
                            if (action.Selection is null) throw new FormatException("Requires selection");
                            this.selectionBegin = action.Selection.start;
                            this.selectionEnd = action.Selection.end;
                            break;
                        
                        case PageAction.ActionType.Insert:
                            if (action.Insertion is null) throw new FormatException("Requires Insertion");
                            int pos = this.selectionBegin;
                            manager.InsertText(action.Insertion.text, pos);
                            break;

                        case PageAction.ActionType.Delete:
                            if (action.Amount is null) throw new FormatException("Requires Delete");
                            manager.DeleteText(this.selectionBegin, action.Amount.amount);
                            break;
                            
                        case PageAction.ActionType.DeleteSelection:
                            manager.ReplaceSelection(this.selectionBegin, this.selectionEnd, "");
                            break;
                            
                    }
                }
            }

            private void Closed()
            {
                manager.RemoveClient(this);
            }
        }
    }
}

    