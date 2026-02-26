using System;
using System.Configuration;
using System.Data;
using MySql.Data.MySqlClient;

namespace ISProposals
{
    public static class DatabaseHelper
    {
        public static string ConnectionString =>
            ConfigurationManager.ConnectionStrings["WorcbenchConnection"].ConnectionString;

        public static DataTable GetAllProposals()
        {
            var dt = new DataTable();
            using (var con = new MySqlConnection(ConnectionString))
            using (var cmd = new MySqlCommand("SELECT Id, Department, Proposal AS ProposalText, Priority, Cost, ImplementationDate FROM proposal ORDER BY Id", con))
            using (var da = new MySqlDataAdapter(cmd))
            {
                da.Fill(dt);
            }
            return dt;
        }

        // Полный набор полей (например, для отчёта или детального просмотра)
        public static DataTable GetAllProposalsFull()
        {
            var dt = new DataTable();
            using (var con = new MySqlConnection(ConnectionString))
            using (var cmd = new MySqlCommand("SELECT * FROM proposal ORDER BY Id", con))
            using (var da = new MySqlDataAdapter(cmd))
            {
                da.Fill(dt);
            }
            return dt;
        }

        public static DataRow GetProposalById(int id)
        {
            var dt = new DataTable();
            using (var con = new MySqlConnection(ConnectionString))
            using (var cmd = new MySqlCommand("SELECT * FROM proposal WHERE Id = @id", con))
            {
                cmd.Parameters.AddWithValue("@id", id);
                using (var da = new MySqlDataAdapter(cmd))
                {
                    da.Fill(dt);
                }
            }
            return dt.Rows.Count > 0 ? dt.Rows[0] : null;
        }

        public static void InsertProposal(Proposal p)
        {
            using (var con = new MySqlConnection(ConnectionString))
            using (var cmd = new MySqlCommand(
                "INSERT INTO proposal (Department, Proposal, Priority, Cost, Justification, ImplementationDate) " +
                "VALUES (@dept, @prop, @prio, @cost, @just, @date)", con))
            {
                cmd.Parameters.AddWithValue("@dept", (object)p.Department ?? DBNull.Value);
                cmd.Parameters.AddWithValue("@prop", (object)p.ProposalText ?? DBNull.Value);
                cmd.Parameters.AddWithValue("@prio", (object)p.Priority ?? DBNull.Value);
                cmd.Parameters.AddWithValue("@cost", p.Cost.HasValue ? (object)p.Cost.Value : DBNull.Value);
                cmd.Parameters.AddWithValue("@just", (object)p.Justification ?? DBNull.Value);
                cmd.Parameters.AddWithValue("@date", p.ImplementationDate.HasValue ? (object)p.ImplementationDate.Value : DBNull.Value);

                con.Open();
                cmd.ExecuteNonQuery();
            }
        }
    }
}