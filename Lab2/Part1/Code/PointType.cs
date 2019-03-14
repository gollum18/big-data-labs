using System;
using System.Data.SqlTypes;
using Microsoft.SqlServer.Server;

namespace CLRUDT_Types
{
    [Microsoft.SqlServer.Server.SqlUserDefinedType(Format.Native,
        IsByteOrdered = true)]
    public struct PointType : INullable
    {
        public bool IsNull { get; private set; }

        public static PointType Null
        {
            get
            {
                PointType point = new PointType
                {
                    IsNull = true
                };
                return point;
            }
        }

        public int X
        {
            get; set;
        }

        public int Y
        {
            get; set;
        }

        public override string ToString()
        {
            return $"{X}:{Y}";
        }

        [SqlMethod(OnNullCall = false)]
        public static PointType Parse(SqlString s)
        {
            if (s.IsNull)
            {
                return Null;
            }

            string[] parts = s.ToString().Split(':');
            if (parts.Length < 2 || !IsInteger(parts[0]) || !IsInteger(parts[1]))
            {
                return Null;
            }
            PointType pt = new PointType
            {
                IsNull = false,
                X = int.Parse(parts[0]),
                Y = int.Parse(parts[1])
            };
            return pt;
        }

        public static bool IsInteger(string s)
        {
            if (s.Equals(null))
            {
                return false;
            }
            try
            {
                int.Parse(s);
                return true;
            }
            catch (Exception)
            {
                return false;
            }
        }
    }
}
