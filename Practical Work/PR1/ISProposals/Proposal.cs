using System;

namespace ISProposals
{
    public class Proposal
    {
        public int Id { get; set; }
        public string Department { get; set; }
        public string ProposalText { get; set; }
        public string Priority { get; set; }
        public decimal? Cost { get; set; }
        public string Justification { get; set; }
        public DateTime? ImplementationDate { get; set; }
    }
}