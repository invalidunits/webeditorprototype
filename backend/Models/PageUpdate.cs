using System.Text.Json.Serialization;

namespace WebEditor.Models
{
    class PageUpdate
    {
        public required string data;
        public required PageAction.SelectionType selection;
    }
}
