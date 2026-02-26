using System;
using System.Data;
using System.Drawing;
using System.Drawing.Printing;
using System.Text;
using System.Windows.Forms;

namespace ISProposals
{
    public class ReportForm : Form
    {
        private TextBox txtReport;
        private Button btnPrint, btnClose;
        private PrintDocument printDoc;
        private string reportText;

        public ReportForm()
        {
            Text = "Отчёт по предложениям";
            Size = new Size(800, 600);
            StartPosition = FormStartPosition.CenterParent;

            txtReport = new TextBox
            {
                Left = 10,
                Top = 10,
                Width = 760,
                Height = 480,
                Multiline = true,
                ReadOnly = true,
                ScrollBars = ScrollBars.Vertical,
                Font = new Font("Consolas", 10)
            };

            btnPrint = new Button { Text = "Печать", Left = 220, Top = 510, Width = 120 };
            btnClose = new Button { Text = "Закрыть", Left = 420, Top = 510, Width = 120 };

            btnPrint.Click += BtnPrint_Click;
            btnClose.Click += (s, e) => Close();

            Controls.Add(txtReport);
            Controls.Add(btnPrint);
            Controls.Add(btnClose);

            printDoc = new PrintDocument();
            printDoc.PrintPage += PrintDoc_PrintPage;

            Load += ReportForm_Load;
        }

        private void ReportForm_Load(object sender, EventArgs e)
        {
            BuildReport();
            txtReport.Text = reportText;
        }

        private void BuildReport()
        {
            var dt = DatabaseHelper.GetAllProposalsFull();
            int total = dt.Rows.Count;
            int highCount = 0;
            decimal totalCost = 0m;

            foreach (DataRow r in dt.Rows)
            {
                if (r["Priority"] != DBNull.Value && r["Priority"].ToString() == "Высокий") highCount++;
                if (r["Cost"] != DBNull.Value)
                {
                    if (decimal.TryParse(r["Cost"].ToString(), out var c)) totalCost += c;
                }
            }

            var sb = new StringBuilder();
            sb.AppendLine("ОТЧЕТ ПО ПРЕДЛОЖЕНИЯМ О РАСШИРЕНИИ ИС");
            sb.AppendLine($"Дата формирования: {DateTime.Now:dd.MM.yyyy HH:mm}");
            sb.AppendLine($"Всего предложений: {total}");
            sb.AppendLine($"Высокоприоритетных: {highCount}");
            sb.AppendLine($"Общая стоимость: {totalCost:N2} ₽");
            sb.AppendLine(new string('=', 80));
            sb.AppendLine();
            sb.AppendLine("СПИСОК ПРЕДЛОЖЕНИЙ:");
            sb.AppendLine();

            foreach (DataRow r in dt.Rows)
            {
                sb.AppendLine($"[ID: {r["Id"]}] {r["Department"]}");
                sb.AppendLine($"Предложение: {r["Proposal"]}");
                sb.AppendLine($"Приоритет: {r["Priority"]} | Стоимость: {(r["Cost"] == DBNull.Value ? "0" : string.Format("{0:N2} ₽", r["Cost"]))}");
                sb.AppendLine($"Срок: {(r["ImplementationDate"] == DBNull.Value ? "" : Convert.ToDateTime(r["ImplementationDate"]).ToString("dd.MM.yyyy"))}");
                sb.AppendLine(new string('-', 80));
            }

            reportText = sb.ToString();
        }

        private void BtnPrint_Click(object sender, EventArgs e)
        {
            using (var dlg = new PrintDialog())
            {
                dlg.Document = printDoc;
                if (dlg.ShowDialog() == DialogResult.OK)
                {
                    try
                    {
                        printDoc.Print();
                    }
                    catch (Exception ex)
                    {
                        MessageBox.Show("Ошибка печати: " + ex.Message, "Ошибка", MessageBoxButtons.OK, MessageBoxIcon.Error);
                    }
                }
            }
        }

        private void PrintDoc_PrintPage(object sender, PrintPageEventArgs e)
        {
            // Простая печать: весь текст в одном столбце, переносы строк.
            var font = new Font("Consolas", 10);
            float left = e.MarginBounds.Left;
            float top = e.MarginBounds.Top;
            float width = e.MarginBounds.Width;
            var sf = new StringFormat();

            // Разбиваем текст на строки и печатаем построчно с переносом по высоте
            var lines = reportText.Split(new[] { "\r\n", "\n" }, StringSplitOptions.None);
            float lineHeight = font.GetHeight(e.Graphics);
            float y = top;
            int lineIndex = 0;
            while (lineIndex < lines.Length)
            {
                if (y + lineHeight > e.MarginBounds.Bottom)
                {
                    // Обрезаем напечатанные строки и сохраним остаток для следующей страницы
                    e.HasMorePages = true;
                    // Для простоты — печатает только первую страницу (если нужно многостранично, надо хранить индекс между вызовами)
                    // Но для небольших отчётов обычно достаточно одной страницы.
                    return;
                }
                e.Graphics.DrawString(lines[lineIndex], font, Brushes.Black, new RectangleF(left, y, width, lineHeight), sf);
                y += lineHeight;
                lineIndex++;
            }

            e.HasMorePages = false;
        }
    }
}