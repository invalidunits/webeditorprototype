using System.Net.WebSockets;
using System.Reflection.Metadata;

namespace WebEditor 
{
    public class Client : IDisposable
    {
        public readonly WebSocket Socket;
        public Client(WebSocket Socket)
        {
            this.Socket = Socket;
            tokenSource = new CancellationTokenSource();
        }

        public readonly CancellationTokenSource tokenSource;

        public bool Recieving { get; private set; } = false;
        void IDisposable.Dispose() => Close();
        ~Client() => Close();
        void Close() => tokenSource.Cancel();


        public async Task RecieveData()
        {
            lock (this)
            {
                if (Recieving) throw new Exception("Already recieving data for this client");
                Recieving = true;
            }


            var buffer = new byte[1024 * 4];
            const int MAX_FAILED_PARSES = 5;
            int failed_parses = 0;
            string closureReason = "Closed Connection";
            WebSocketCloseStatus status = WebSocketCloseStatus.NormalClosure;

            try
            {
                while (Socket.State == WebSocketState.Open)
                {
                    WebSocketReceiveResult result = await Socket.ReceiveAsync(buffer, tokenSource.Token);
                    if (result.MessageType == WebSocketMessageType.Close) break; 
                    if (tokenSource.IsCancellationRequested) break;
                    if (result.MessageType == WebSocketMessageType.Text) try
                    {
                        Parse(result, new ReadOnlySpan<byte>(buffer, 0, result.Count));
                        failed_parses = 0;
                    }
                    catch (Exception ex)
                    {
                        ++failed_parses;
                        if (failed_parses > MAX_FAILED_PARSES) throw new AggregateException("Failed repeatedly to parse messages", ex);
                    }
                }
            }
            catch (Exception except)
            {
                closureReason = except.ToString();
                status = WebSocketCloseStatus.InvalidPayloadData;
            }
            
            
            Recieving = false;
            Closed();
            if (!tokenSource.IsCancellationRequested) Close();
            if (Socket.State == WebSocketState.Open) 
            {
                await Socket.CloseAsync(status, closureReason, CancellationToken.None);
            }
            else
            {
                Socket.Abort();
            }
        }

        public event Action<WebSocketReceiveResult, ReadOnlySpan<byte>> Parse = delegate { };
        public event Action Closed = delegate { };
    }
}