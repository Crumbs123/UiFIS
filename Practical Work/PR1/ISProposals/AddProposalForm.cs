using System;
using System.Drawing;
using System.Globalization;
using System.Windows.Forms;

namespace ISProposals
{
    public class AddProposalForm : Form
    {
        private TextBox txtDepartment, txtProposal, txtCost, txtJustification;
        private ComboBox cbPriority;
        private DateTimePicker dpImplementation;
        private Button btnSave, btnCancel;

        public AddProposalForm()
        {
            Text = "Добавление нового предложения";
            Size = new Size(600, 420);
            StartPosition = FormStartPosition.CenterParent;
            FormBorderStyle = FormBorderStyle.FixedDialog;
            MaximizeBox = false;
            MinimizeBox = false;

            var lblDept = new Label { Text = "Подразделение:", Left = 20, Top = 20, Width = 120 };
            txtDepartment = new TextBox { Left = 150, Top = 18, Width = 400 };

            var lblProp = new Label { Text = "Предложение:", Left = 20, Top = 60, Width = 120 };
            txtProposal = new TextBox { Left = 150, Top = 58, Width = 400 };

            var lblPriority = new Label { Text = "Приоритет:", Left = 20, Top = 100, Width = 120 };
            cbPriority = new ComboBox { Left = 150, Top = 98, Width = 200, DropDownStyle = ComboBoxStyle.DropDownList };
            cbPriority.Items.AddRange(new[] { "Высокий", "Средний", "Низкий" });
            cbPriority.SelectedIndex = 1;

            var lblCost = new Label { Text = "Примерная стоимость:", Left = 20, Top = 140, Width = 120 };
            txtCost = new TextBox { Left = 150, Top = 138, Width = 200 };

            var lblJust = new Label { Text = "Обоснование:", Left = 20, Top = 180, Width = 120 };
            txtJustification = new TextBox { Left = 150, Top = 178, Width = 400, Height = 100, Multiline = true, ScrollBars = ScrollBars.Vertical };

            var lblDate = new Label { Text = "Срок реализации:", Left = 20, Top = 290, Width = 120 };
            dpImplementation = new DateTimePicker { Left = 150, Top = 288, Width = 200, Format = DateTimePickerFormat.Short, Value = DateTime.Today };

            btnSave = new Button { Text = "Сохранить", Left = 150, Top = 330, Width = 120, BackColor = Color.LightGreen };
            btnCancel = new Button { Text = "Отмена", Left = 300, Top = 330, Width = 120, BackColor = Color.LightCoral };

            btnSave.Click += BtnSave_Click;
            btnCancel.Click += (s, e) => DialogResult = DialogResult.Cancel;

            Controls.AddRange(new Control[] {
                lblDept, txtDepartment,
                lblProp, txtProposal,
                lblPriority, cbPriority,
                lblCost, txtCost,
                lblJust, txtJustification,
                lblDate, dpImplementation,
                btnSave, btnCancel
            });
        }

        private void BtnSave_Click(object sender, EventArgs e)
        {
            // Валидация простая
            if (string.IsNullOrWhiteSpace(txtDepartment.Text))
            {
                MessageBox.Show("Укажите подразделение.", "Ошибка", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                txtDepartment.Focus();
                return;
            }
            if (string.IsNullOrWhiteSpace(txtProposal.Text))
            {
                MessageBox.Show("Укажите текст предложения.", "Ошибка", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                txtProposal.Focus();
                return;
            }

            decimal? cost = null;
            if (!string.IsNullOrWhiteSpace(txtCost.Text))
            {
                if (decimal.TryParse(txtCost.Text, NumberStyles.Any, CultureInfo.CurrentCulture, out var c))
                    cost = c;
                else
                {
                    MessageBox.Show("Неверный формат стоимости.", "Ошибка", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                    txtCost.Focus();
                    return;
                }
            }

            var p = new Proposal
            {
                Department = txtDepartment.Text.Trim(),
                ProposalText = txtProposal.Text.Trim(),
                Priority = cbPriority.SelectedItem?.ToString() ?? "Средний",
                Cost = cost,
                Justification = txtJustification.Text.Trim(),
                ImplementationDate = dpImplementation.Value.Date
            };

            try
            {
                DatabaseHelper.InsertProposal(p);
                DialogResult = DialogResult.OK;
            }
            catch (Exception ex)
            {
                MessageBox.Show("Ошибка при сохранении: " + ex.Message, "Ошибка", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }
    }
}