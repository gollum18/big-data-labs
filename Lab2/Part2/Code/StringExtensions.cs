using System.Text.RegularExpressions;

namespace CLRUDF
{
    public static class StringExtensions
    {
        public static string SafeReplace(this string input, string find, string replace, bool matchWholeWord) =>
            Regex.Replace(input, matchWholeWord ? string.Format(@"\b{0}\b", find) : find, replace);
    }
}
