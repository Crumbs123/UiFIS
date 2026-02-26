using System;
using System.Data;
using System.Drawing;
using System.Windows.Forms;

namespace ISProposals
{
    public class DetailsForm : Form
    {
        private TextBox txtDetails;
        private Button btnClose;
        private int proposalId;

        public DetailsForm(int id)
        {
            proposalId = id;
            Text = "Детальная информация о предложении";
            Size = new Size(600, 420);
            StartPosition = FormStartPosition.CenterParent;

            txtDetails = new TextBox
            {
                Left = 10,
                Top = 10,
                Width = 560,
                Height = 320,
                Multiline = true,
                ReadOnly = true,
                ScrollBars = ScrollBars.Vertical
            };

            btnClose = new Button { Text = "Закрыть", Left = 250, Top = 340, Width = 100 };
            btnClose.Click += (s, e) => Close();

            Controls.Add(txtDetails);
            Controls.Add(btnClose);

            Load += DetailsForm_Load;
        }

        private void DetailsForm_Load(object sender, EventArgs e)
        {
            try
            {
                var row = DatabaseHelper.GetProposalById(proposalId);
                if (row == null)
                {
                    txtDetails.Text = "Предложение не найдено.";
                    return;
                }

                var lines = new System.Text.StringBuilder();
                lines.AppendLine("ПОДРОБНАЯ ИНФОРМАЦИЯ О ПРЕДЛОЖЕНИИ");
                lines.AppendLine();
                lines.AppendLine($"ID: {row["Id"]}");
                lines.AppendLine($"Подразделение: {row["Department"]}");
                lines.AppendLine($"Предложение: {row["Proposal"]}");
                lines.AppendLine($"Приоритет: {row["Priority"]}");
                lines.AppendLine($"Стоимость: {(row["Cost"] == DBNull.Value ? "" : string.Format("{0:N2} ₽", row["Cost"]))}");
                lines.AppendLine($"Срок реализации: {(row["ImplementationDate"] == DBNull.Value ? "" : Convert.ToDateTime(row["ImplementationDate"]).ToString("dd.MM.yyyy"))}");
                lines.AppendLine();
                lines.AppendLine("ОБОСНОВАНИЕ:");
                lines.AppendLine(row["Justification"] == DBNull.Value ? "" : row["Justification"].ToString());

                txtDetails.Text = lines.ToString();
            }
            catch (Exception ex)
            {
                txtDetails.Text = "Ошибка загрузки: " + ex.Message;
            }
        }
    }
}