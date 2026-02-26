using System;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using System.Windows.Forms.DataVisualization.Charting;

namespace ReliabilityApp
{
    public class Form1 : Form
    {
        private TabControl tabControl;

        // ===== Task 1 =====
        private DataGridView dgvTask1;
        private Button btnCalc1;
        private RichTextBox rtbTask1;
        private Chart chartTask1;

        // ===== Task 2 =====
        private DataGridView dgvTask2;
        private Button btnCalc2;
        private RichTextBox rtbTask2;

        // ===== Task 3 =====
        private DataGridView dgvTask3;
        private Button btnCalc3;
        private RichTextBox rtbTask3;

       
   
        public Form1()
        {
            Text = "Практическая работа №2 — Показатели безотказности";
            Size = new Size(1100, 650);
            StartPosition = FormStartPosition.CenterScreen;
            Font = new Font("Segoe UI", 10);

            tabControl = new TabControl { Dock = DockStyle.Fill };
            tabControl.TabPages.Add(CreateTask1Tab());
            tabControl.TabPages.Add(CreateTask2Tab());
            tabControl.TabPages.Add(CreateTask3Tab());
            Controls.Add(tabControl);
        }

        // ================= TASK 1 =================
        private TabPage CreateTask1Tab()
        {
            var tab = new TabPage("Задание 1");

            dgvTask1 = new DataGridView
            {
                Location = new Point(20, 20),
                Size = new Size(350, 200),
                AllowUserToAddRows = false,
                ReadOnly = true
            };
            dgvTask1.Columns.Add("n", "№ отказа");
            dgvTask1.Columns.Add("t", "Время до отказа, ч");
            double[] t = { 185, 342, 268, 220, 96, 102 };
            for (int i = 0; i < t.Length; i++)
                dgvTask1.Rows.Add(i + 1, t[i]);

            btnCalc1 = new Button
            {
                Text = "Рассчитать MTBF",
                Location = new Point(20, 240),
                Size = new Size(180, 40)
            };
            btnCalc1.Click += CalcTask1;

            rtbTask1 = new RichTextBox
            {
                Location = new Point(20, 300),
                Size = new Size(500, 250),
                ReadOnly = true
            };

            chartTask1 = new Chart
            {
                Location = new Point(400, 20),
                Size = new Size(650, 260)
            };
            var area = new ChartArea();
            chartTask1.ChartAreas.Add(area);
            var series = new Series { ChartType = SeriesChartType.Column };
            chartTask1.Series.Add(series);

            tab.Controls.Add(dgvTask1);
            tab.Controls.Add(btnCalc1);
            tab.Controls.Add(rtbTask1);
            tab.Controls.Add(chartTask1);
            return tab;
        }

        private void CalcTask1(object sender, EventArgs e)
        {
            double[] t = { 185, 342, 268, 220, 96, 102 };
            double sum = t.Sum();
            double mtbf = sum / t.Length;

            var sb = new StringBuilder();
            sb.AppendLine("ИСХОДНЫЕ ДАННЫЕ:");
            for (int i = 0; i < t.Length; i++)
                sb.AppendLine($"Отказ {i + 1}: t{i + 1} = {t[i]} ч");

            sb.AppendLine("\nРЕШЕНИЕ:");
            sb.AppendLine("Σt = " + string.Join(" + ", t) + " = " + sum + " ч");
            sb.AppendLine("n = " + t.Length);
            sb.AppendLine("MTBF = Σt / n");
            sb.AppendLine($"MTBF = {sum} / {t.Length} = {mtbf:F2} ч");

            rtbTask1.Text = sb.ToString();

            chartTask1.Series[0].Points.Clear();
            for (int i = 0; i < t.Length; i++)
                chartTask1.Series[0].Points.AddXY(i + 1, t[i]);
        }

        // ================= TASK 2 =================
        private TabPage CreateTask2Tab()
        {
            var tab = new TabPage("Задание 2");

            dgvTask2 = new DataGridView
            {
                Location = new Point(20, 20),
                Size = new Size(450, 180),
                AllowUserToAddRows = false,
                ReadOnly = true
            };
            dgvTask2.Columns.Add("sys", "Система");
            dgvTask2.Columns.Add("t", "Время работы, ч");
            dgvTask2.Columns.Add("n", "Число отказов");
            dgvTask2.Columns.Add("mtbf", "MTBF, ч");

            dgvTask2.Rows.Add("1", 358, 4, "");
            dgvTask2.Rows.Add("2", 385, 3, "");
            dgvTask2.Rows.Add("3", 400, 2, "");

            btnCalc2 = new Button
            {
                Text = "Рассчитать",
                Location = new Point(20, 220),
                Size = new Size(160, 40)
            };
            btnCalc2.Click += CalcTask2;

            rtbTask2 = new RichTextBox
            {
                Location = new Point(20, 280),
                Size = new Size(600, 260),
                ReadOnly = true
            };

            tab.Controls.Add(dgvTask2);
            tab.Controls.Add(btnCalc2);
            tab.Controls.Add(rtbTask2);
            return tab;
        }

        private void CalcTask2(object sender, EventArgs e)
        {
            double[] t = { 358, 385, 400 };
            int[] n = { 4, 3, 2 };

            var sb = new StringBuilder();
            sb.AppendLine("ИСХОДНЫЕ ДАННЫЕ:");
            for (int i = 0; i < 3; i++)
            {
                double mtbf = t[i] / n[i];
                dgvTask2.Rows[i].Cells[3].Value = mtbf.ToString("F2");
                sb.AppendLine($"Система {i + 1}: t = {t[i]} ч, n = {n[i]}, MTBF = {mtbf:F2} ч");
            }

            sb.AppendLine("\nОБЩИЙ РАСЧЕТ:");
            double sumT = t.Sum();
            int sumN = n.Sum();
            double totalMtbf = sumT / sumN;
            sb.AppendLine($"Σt = {sumT} ч");
            sb.AppendLine($"Σn = {sumN}");
            sb.AppendLine($"MTBFобщ = Σt / Σn = {totalMtbf:F2} ч");

            rtbTask2.Text = sb.ToString();
        }

        // ================= TASK 3 =================
        private TabPage CreateTask3Tab()
        {
            var tab = new TabPage("Задание 3 (Вариант 1)");

            dgvTask3 = new DataGridView
            {
                Location = new Point(20, 20),
                Size = new Size(500, 200),
                AllowUserToAddRows = false,
                ReadOnly = true
            };
            dgvTask3.Columns.Add("sys", "Система");
            dgvTask3.Columns.Add("t0", "T₀, ч");
            dgvTask3.Columns.Add("tv", "Tᵥ, ч");
            dgvTask3.Columns.Add("kg", "Kг");

            dgvTask3.Rows.Add("1", 24, 16, "");
            dgvTask3.Rows.Add("2", 400, 32, "");

            btnCalc3 = new Button
            {
                Text = "Выполнить анализ",
                Location = new Point(20, 240),
                Size = new Size(180, 40)
            };
            btnCalc3.Click += CalcTask3;

            rtbTask3 = new RichTextBox
            {
                Location = new Point(20, 300),
                Size = new Size(700, 260),
                ReadOnly = true
            };

            tab.Controls.Add(dgvTask3);
            tab.Controls.Add(btnCalc3);
            tab.Controls.Add(rtbTask3);
            return tab;
        }

        private void CalcTask3(object sender, EventArgs e)
        {
            double[] t0 = { 24, 400 };
            double[] tv = { 16, 32 };

            var sb = new StringBuilder();
            sb.AppendLine("РАСЧЕТ КОЭФФИЦИЕНТА ГОТОВНОСТИ:\n");

            double bestKg = 0;
            int bestSystem = 0;

            for (int i = 0; i < 2; i++)
            {
                double kg = t0[i] / (t0[i] + tv[i]);
                dgvTask3.Rows[i].Cells[3].Value = kg.ToString("F3");

                sb.AppendLine($"Система {i + 1}:");
                sb.AppendLine($"Kг = T₀ / (T₀ + Tᵥ) = {t0[i]} / ({t0[i]} + {tv[i]}) = {kg:F3}\n");

                if (kg > bestKg)
                {
                    bestKg = kg;
                    bestSystem = i + 1;
                }
            }

            sb.AppendLine($"ВЫВОД: наиболее надежной является система {bestSystem}, так как имеет максимальный коэффициент готовности.");
            rtbTask3.Text = sb.ToString();
        }
    }
}
