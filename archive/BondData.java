import java.time.LocalDate;
import java.time.temporal.ChronoUnit;
import java.time.format.DateTimeFormatter;
public class BondData {
    private LocalDate recordDate;
    private String securityType;
    private String securityClass;
    private String bondIdentifier;
    private Double interestRate;
    private Double yield;
    private LocalDate issuedDate;
    private LocalDate maturityDate;
    private LocalDate interestPayableDate;
    private Double issuedAmount;
    private Double amountAdjustedForInflation;
    private Double redeemedAmount;
    private Double outstandingAmount;

    public BondData(LocalDate recordDate, String securityType, String securityClass,
                    String bondIdentifier, Double interestRate, Double yield,
                    LocalDate issuedDate, LocalDate maturityDate,
                    LocalDate interestPayableDate, Double issuedAmount,
                    Double amountAdjustedForInflation, Double redeemedAmount,
                    Double outstandingAmount) {
        this.recordDate = recordDate;
        this.securityType = securityType;
        this.securityClass = securityClass;
        this.bondIdentifier = bondIdentifier;
        this.interestRate = interestRate;
        this.yield = yield;
        this.issuedDate = issuedDate;
        this.maturityDate = maturityDate;
        this.interestPayableDate = interestPayableDate;
        this.issuedAmount = issuedAmount;
        this.amountAdjustedForInflation = amountAdjustedForInflation;
        this.redeemedAmount = redeemedAmount;
        this.outstandingAmount = outstandingAmount;
    }

    public BondData(String bondIdentifier, LocalDate issuedDate, LocalDate maturityDate, Double issuedAmount, Double yield) {
        this(null, null, null, bondIdentifier, null, yield, issuedDate, maturityDate, null,
             issuedAmount, null, null, null);
    }


	public static void main( String[] args) {

		DateTimeFormatter inputFormatter = DateTimeFormatter.ofPattern("M/d/yy");
        LocalDate localDate = LocalDate.parse("6/30/23", inputFormatter);

		LocalDate date2 = LocalDate.parse("2021-05-05");

		long daysBetween = ChronoUnit.DAYS.between(localDate, date2);

		System.out.println(daysBetween);

	}

	public String getDuplicateIdentifer() {
		return issuedDate + ":" + issuedAmount + ":" + yield;
	}

	public Double getBondContractLength() {
		if (issuedDate == null || maturityDate == null) {
			return null;
		}
		return Double.parseDouble(Long.toString(ChronoUnit.DAYS.between(issuedDate, maturityDate)));
	}

    public LocalDate getRecordDate() {
        return recordDate;
    }

    public void setRecordDate(LocalDate recordDate) {
        this.recordDate = recordDate;
    }

    public String getSecurityType() {
        return securityType;
    }

    public void setSecurityType(String securityType) {
        this.securityType = securityType;
    }

    public String getSecurityClass() {
        return securityClass;
    }

    public void setSecurityClass(String securityClass) {
        this.securityClass = securityClass;
    }

    public String getBondIdentifier() {
        return bondIdentifier;
    }

    public void setBondIdentifier(String bondIdentifier) {
        this.bondIdentifier = bondIdentifier;
    }

    public Double getInterestRate() {
        return interestRate;
    }

    public void setInterestRate(double interestRate) {
        this.interestRate = interestRate;
    }

    public Double getYield() {
        return yield;
    }

    public void setYield(double yield) {
        this.yield = yield;
    }

    public LocalDate getIssuedDate() {
        return issuedDate;
    }

    public void setIssuedDate(LocalDate issuedDate) {
        this.issuedDate = issuedDate;
    }

    public LocalDate getMaturityDate() {
        return maturityDate;
    }

    public void setMaturityDate(LocalDate maturityDate) {
        this.maturityDate = maturityDate;
    }

    public LocalDate getInterestPayableDate() {
        return interestPayableDate;
    }

    public void setInterestPayableDate(LocalDate interestPayableDate) {
        this.interestPayableDate = interestPayableDate;
    }

    public Double getIssuedAmount() {
        return issuedAmount;
    }

    public void setIssuedAmount(double issuedAmount) {
        this.issuedAmount = issuedAmount;
    }

    public Double getAmountAdjustedForInflation() {
        return amountAdjustedForInflation;
    }

    public void setAmountAdjustedForInflation(double amountAdjustedForInflation) {
        this.amountAdjustedForInflation = amountAdjustedForInflation;
    }

    public Double getRedeemedAmount() {
        return redeemedAmount;
    }

    public void setRedeemedAmount(double redeemedAmount) {
        this.redeemedAmount = redeemedAmount;
    }

    public Double getOutstandingAmount() {
        return outstandingAmount;
    }

    public void setOutstandingAmount(double outstandingAmount) {
        this.outstandingAmount = outstandingAmount;
    }


}