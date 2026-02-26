using System;
using System.Data;
using System.Drawing;
using System.Windows.Forms;

namespace ISProposals
{
    public class MainForm : Form
    {
        private DataGridView dgv;
        private Button btnAdd, btnDetails, btnReport, btnExit;

        public MainForm()
        {
            Text = "Предложения по расширению ИС";
            Size = new Size(900, 520);
            StartPosition = FormStartPosition.CenterScreen;

            dgv = new DataGridView
            {
                Dock = DockStyle.Top,
                Height = 340,
                ReadOnly = true,
                SelectionMode = DataGridViewSelectionMode.FullRowSelect,
                AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.Fill,
                AllowUserToAddRows = false
            };
            Controls.Add(dgv);

            btnAdd = new Button { Text = "Добавить предложение", Left = 20, Top = 360, Width = 200 };
            btnDetails = new Button { Text = "Просмотр деталей", Left = 240, Top = 360, Width = 160 };
            btnReport = new Button { Text = "Сформировать отчёт", Left = 420, Top = 360, Width = 160 };
            btnExit = new Button { Text = "Выход", Left = 760, Top = 360, Width = 80 };

            btnAdd.Click += BtnAdd_Click;
            btnDetails.Click += BtnDetails_Click;
            btnReport.Click += BtnReport_Click;
            btnExit.Click += (s, e) => Close();

            Controls.AddRange(new Control[] { btnAdd, btnDetails, btnReport, btnExit });

            Load += MainForm_Load;
        }

        private void MainForm_Load(object sender, EventArgs e)
        {
            LoadData();
        }

        private void LoadData()
        {
            try
            {
                var dt = DatabaseHelper.GetAllProposals();
                dgv.DataSource = dt;

                if (dgv.Columns.Contains("ProposalText"))
                    dgv.Columns["ProposalText"].HeaderText = "Предложение";
                if (dgv.Columns.Contains("Department"))
                    dgv.Columns["Department"].HeaderText = "Подразделение";
                if (dgv.Columns.Contains("Priority"))
                    dgv.Columns["Priority"].HeaderText = "Приоритет";
                if (dgv.Columns.Contains("Cost"))
                {
                    dgv.Columns["Cost"].HeaderText = "Стоимость";
                    dgv.Columns["Cost"].DefaultCellStyle.Format = "N2";
                }
                if (dgv.Columns.Contains("ImplementationDate"))
                    dgv.Columns["ImplementationDate"].HeaderText = "Срок реализации";
            }
            catch (Exception ex)
            {
                MessageBox.Show("Ошибка загрузки данных: " + ex.Message, "Ошибка", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void BtnAdd_Click(object sender, EventArgs e)
        {
            using (var f = new AddProposalForm())
            {
                if (f.ShowDialog() == DialogResult.OK)
                {
                    LoadData();
                }
            }
        }

        private int? GetSelectedId()
        {
            if (dgv.SelectedRows.Count == 0) return null;
            var row = dgv.SelectedRows[0];
            if (row.Cells["Id"].Value == null) return null;
            return Convert.ToInt32(row.Cells["Id"].Value);
        }

        private void BtnDetails_Click(object sender, EventArgs e)
        {
            var id = GetSelectedId();
            if (id == null)
            {
                MessageBox.Show("Выберите предложение в списке.", "Внимание", MessageBoxButtons.OK, MessageBoxIcon.Information);
                return;
            }
            using (var f = new DetailsForm(id.Value))
            {
                f.ShowDialog();
            }
        }

        private void BtnReport_Click(object sender, EventArgs e)
        {
            using (var f = new ReportForm())
            {
                f.ShowDialog();
            }
        }
    }
}