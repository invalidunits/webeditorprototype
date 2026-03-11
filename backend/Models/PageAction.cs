
using Newtonsoft.Json;
namespace WebEditor.Models
{
    struct PageAction
    {
        public enum ActionType 
        {
            Select,
            Insert, 
            Delete,
            DeleteSelection
        }

        public class SelectionType
        {
            [JsonRequired]
            public int start;
            [JsonRequired]
            public int end;
        }

        public class InsertType
        {
            [JsonRequired]
            public string text;
        }

        public class AmountType
        {
            [JsonRequired]
            public int amount;
        }

        [JsonRequired]
        public ActionType Type;
        public AmountType? Amount;
        public SelectionType? Selection;
        public InsertType? Insertion;
    }
}