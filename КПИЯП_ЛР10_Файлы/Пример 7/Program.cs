using System;
using System.Collections.Generic;
using System.Text;

namespace ConsoleApplication1
{
    class Font
    {
        string TypeFont;
        short FontSize;

        public Font()
        {
            TypeFont = "Arial";
            FontSize = 12;
        }

        public Font(string TypeFont, short FontSize)
        {
            this.TypeFont = TypeFont;
            this.FontSize = FontSize;
        }

        public string typeFont
        {
            get
            {
                return TypeFont;
            }

            set
            {
                TypeFont = value;
            }
        }

        public short fontSize
        {
            get
            {
                return FontSize;
            }

            set
            {
                FontSize = value;
            }
        }

        public virtual string FontInfo(Font obj)
        {
            string s = "РРЅС„РѕСЂРјР°С†РёСЏ Рѕ С€СЂРёС„С‚Рµ: \n------------------\n\n" +
                "РўРёРї С€СЂРёС„С‚Р°: " + typeFont +
                "\nР Р°Р·РјРµСЂ С€СЂРёС„С‚Р°: " + fontSize + "\n";
            return s;
        }
    }

    class ColorFont : Font
    {
        byte Color;

        public ColorFont(byte Color, string TypeFont, short FontSize)
            : base(TypeFont, FontSize)
        {
            this.Color = Color;
        }

        public override string FontInfo(Font obj)
        {
            return base.FontInfo(obj) + "Р¦РІРµС‚ С€СЂРёС„С‚Р°: " + Color + "\n";
        }

        public virtual byte color
        {
            set
            {
                Color = value;
            }

            get
            {
                return Color;
            }
        }
    }

    class GradientColorFont : ColorFont
    {
        char TypeGradient;

        public GradientColorFont(char TypeGradient, byte Color, string TypeFont, short FontSize) :
            base(Color, TypeFont, FontSize)
        {
            this.TypeGradient = TypeGradient;
        }

        public override string FontInfo(Font obj)
        {
            return base.FontInfo(obj) + "РўРёРї РіСЂР°РґРёРµРЅС‚Р°: " + TypeGradient + "\n\n";
        }

        public override byte color
        {
            get
            {
                return base.color;
            }
            set
            {
                if (value < 10)
                    base.color = 0;
                else
                    base.color = (byte)(value - 0x0A);
            }
        }
    }

    class FontStyle : Font
    {
        string style;

        public FontStyle(string style, string TypeFont, short FontSize) : base(TypeFont, FontSize)
        {
            this.style = style;
        }
    }

    class Program
    {
        static void Main()
        {
            ColorFont font1 = new ColorFont(Color: 0xCF, TypeFont: "MS Trebuchet", FontSize: 16);
            Console.WriteLine(font1.FontInfo(font1));

            GradientColorFont font2 = new GradientColorFont(Color: 0xFF, TypeFont: "Times New Roman", FontSize: 10, TypeGradient: 'R');
            Console.WriteLine(font2.FontInfo(font2));

            font2.color = 0x2F;
            Console.ForegroundColor = ConsoleColor.Green;
            Console.WriteLine("Р’РёРґРѕРёР·РјРµРЅРµРЅРЅС‹Р№ С†РІРµС‚ font2");
            Console.ForegroundColor = ConsoleColor.Gray;
            Console.WriteLine(font2.FontInfo(font2));

            FontStyle font3 = new FontStyle(style: "oblique", TypeFont: "Calibri", FontSize: 16);
            Console.WriteLine(font3.FontInfo(font3));
        }
    }
}
