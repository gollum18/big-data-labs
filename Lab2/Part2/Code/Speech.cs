using System;
using System.Collections.Generic;
using System.Data.SqlTypes;
using Microsoft.SqlServer.Server;

namespace CLRUDF
{
    public class Speech
    {
        public static readonly string[] SPLIT_PARTS = {
            "FIRSTNAME=", "LASTNAME=", "MONTH=", "DAY=",
            "YEAR=", "WEBLINK=", "FILELINK=", "SPEECH=" };

        private Dictionary<string, int> DocumentFrequency = new Dictionary<string, int>();

        public string Firstname { get; set; }

        public string Lastname { get; set; }

        public string Month { get; set; }

        public int Day { get; set; }

        public int Year { get; set; }

        public string Weblink { get; set; }

        public string Filelink { get; set; }

        public string Text { get; set; }

        public bool IsNull { get; private set; }

        public static Speech Null
        {
            get
            {
                Speech speech = new Speech
                {
                    IsNull = true
                };
                return speech;
            }
        }

        public override string ToString()
        {
            return $"FIRSTNAME={Firstname}LASTNAME={Lastname}MONTH={Month}" +
                $"DAY={Day}YEAR={Year}WEBLINK={Weblink}FILELINK={Filelink}" +
                $"SPEECH={Text}";
        }

        [SqlMethod(OnNullCall = false)]
        public static Speech Parse(SqlString s)
        {
            if (s.IsNull)
            {
                return Null;
            }

            string[] parts = s.ToString().Split(SPLIT_PARTS, StringSplitOptions.None);

            if (parts.Length < 8)
            {
                return Null;
            }

            if (!int.TryParse(parts[3], out int day))
            {
                return Null;
            }

            if (!int.TryParse(parts[4], out int year))
            {
                return Null;
            }

            Speech speech = new Speech
            {
                IsNull = false,
                Firstname = parts[0],
                Lastname = parts[1],
                Month = parts[2],
                Day = day,
                Year = year,
                Weblink = parts[5],
                Filelink = parts[6],
                Text = parts[7]
            };
            return speech;
        }

        public void UpdateFrequency(string word)
        {
            if (DocumentFrequency.ContainsKey(word))
            {
                DocumentFrequency[word]++;
            }
            else
            {
                DocumentFrequency[word] = 1;
            }
        }

        public override bool Equals(object obj)
        {
            if (!(obj is Speech))
            {
                return false;
            }

            var speech = (Speech)obj;
            return Firstname == speech.Firstname &&
                   Lastname == speech.Lastname &&
                   Month == speech.Month &&
                   Day == speech.Day &&
                   Year == speech.Year;
        }

        public override int GetHashCode()
        {
            var hashCode = 480983858;
            hashCode = hashCode * -1521134295 + EqualityComparer<string>.Default.GetHashCode(Firstname);
            hashCode = hashCode * -1521134295 + EqualityComparer<string>.Default.GetHashCode(Lastname);
            hashCode = hashCode * -1521134295 + EqualityComparer<string>.Default.GetHashCode(Month);
            hashCode = hashCode * -1521134295 + Day.GetHashCode();
            hashCode = hashCode * -1521134295 + Year.GetHashCode();
            return hashCode;
        }
    }
}
