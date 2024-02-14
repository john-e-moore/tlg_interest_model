import java.util.List;
import java.util.ArrayList;
import java.util.Stack;
import java.util.Scanner;
import java.io.*;
import java.util.HashMap;
import java.util.Map;
import java.util.Iterator;
import java.util.Set;
import java.util.*;
import java.util.Random;
import java.lang.Math;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;

public class TreasuryBondsParse {

	public static void main( String[] args) throws Exception {
		TreasuryBondsParse compiler = new TreasuryBondsParse();

		ArrayList<BondData> bonds = compiler.parseFile("finishedUpdatedCSVTreasuryData.csv");
		
		ArrayList<BondData> thinnedBondList = compiler.thinReissuedBonds(bonds);

		ArrayList<BondData> finalizedBonds = compiler.deleteDuplicates(thinnedBondList); 

		double debtToPublic = 26938517614684.59 / 100000;
		for (int i = 0; i < finalizedBonds.size(); i++) {
			finalizedBonds.get(i).setIssuedAmount(finalizedBonds.get(i).getIssuedAmount() * debtToPublic);
		}
		System.out.println(compiler.calculateTotalOutstandingInterestOneYear(finalizedBonds));
		//compiler.calculateTotalInterestPaidUntil2050BaseAssumption(finalizedBonds);

		/*
		ArrayList<BondData> larryBondList = new ArrayList<BondData>();
		for (int i = 0; i < finalizedBonds.size(); i++) {
			//System.out.println(finalizedBonds.get(i).getBondContractLength());
			if (finalizedBonds.get(i).getBondContractLength() > 0 && finalizedBonds.get(i).getBondContractLength() < 3000) {
				larryBondList.add(finalizedBonds.get(i));
			}
		}

		double twoYearMature2005 = 0;
		double threeYearMature2005 = 0;
		double fiveYearMature2005 = 0;
		double sevenYearMature2005 = 0;
		// 1 year
		double twoYearMature2006 = 0;
		double threeYearMature2006 = 0;
		double fiveYearMature2006 = 0;
		double sevenYearMature2006 = 0;
		// 1 year
		double twoYearMature2007 = 0;
		double threeYearMature2007 = 0;
		double fiveYearMature2007 = 0;
		double sevenYearMature2007 = 0;
		// 1 year
		double twoYearMature2008 = 0;
		double threeYearMature2008 = 0;
		double fiveYearMature2008 = 0;
		double sevenYearMature2008 = 0;
		// 1 year
		double twoYearMature2009 = 0;
		double threeYearMature2009 = 0;
		double fiveYearMature2009 = 0;
		double sevenYearMature2009 = 0;
		// 1 year
		double twoYearMature2010 = 0;
		double threeYearMature2010 = 0;
		double fiveYearMature2010 = 0;
		double sevenYearMature2010 = 0;
		//1 year
		double twoYearMature2011 = 0;
		double threeYearMature2011 = 0;
		double fiveYearMature2011 = 0;
		double sevenYearMature2011 = 0;
		//1 year
		double twoYearMature2012 = 0;
		double threeYearMature2012 = 0;
		double fiveYearMature2012 = 0;
		double sevenYearMature2012 = 0;
		// 1 year
		double twoYearMature2013 = 0;
		double threeYearMature2013 = 0;
		double fiveYearMature2013 = 0;
		double sevenYearMature2013 = 0;
		//1 year
		double twoYearMature2014 = 0;
		double threeYearMature2014 = 0;
		double fiveYearMature2014 = 0;
		double sevenYearMature2014 = 0;
		// 1 year
		double twoYearMature2015 = 0;
		double threeYearMature2015 = 0;
		double fiveYearMature2015 = 0;
		double sevenYearMature2015 = 0;
		// 1 year
		double twoYearMature2016 = 0;
		double threeYearMature2016 = 0;
		double fiveYearMature2016 = 0;
		double sevenYearMature2016 = 0;
		// 1 year
		double twoYearMature2017 = 0;
		double threeYearMature2017 = 0;
		double fiveYearMature2017 = 0;
		double sevenYearMature2017 = 0;
		//1 year
		double twoYearMature2018 = 0;
		double threeYearMature2018 = 0;
		double fiveYearMature2018 = 0;
		double sevenYearMature2018 = 0;
		// 1 year
		double twoYearMature2019 = 0;
		double threeYearMature2019 = 0;
		double fiveYearMature2019 = 0;
		double sevenYearMature2019 = 0;
		//
		double twoYearMature2020 = 0;
		double threeYearMature2020 = 0;
		double fiveYearMature2020 = 0;
		double sevenYearMature2020 = 0;
		//
		double twoYearMature2021 = 0;
		double threeYearMature2021 = 0;
		double fiveYearMature2021 = 0;
		double sevenYearMature2021 = 0;
		//
		double twoYearMature2022 = 0;
		double twoYearMature2023 = 0;
		double twoYearMature2024 = 0;
		double twoYearMature2025 = 0;
		double twoYearMature2026 = 0;
		double threeYearMature2022 = 0;
		double threeYearMature2023 = 0;
		double threeYearMature2024 = 0;
		double threeYearMature2025 = 0;
		double threeYearMature2026 = 0;
		double fiveYearMature2022 = 0;
		double fiveYearMature2023 = 0;
		double fiveYearMature2024 = 0;
		double fiveYearMature2025 = 0;
		double fiveYearMature2026 = 0;
		double sevenYearMature2022 = 0;
		double sevenYearMature2023 = 0;
		double sevenYearMature2024 = 0;
		double sevenYearMature2025 = 0;
		double sevenYearMature2026 = 0;
		for (int i = 0; i < larryBondList.size(); i++) {
			if (larryBondList.get(i).getMaturityDate().getYear() == 2005) {
				if (larryBondList.get(i).getBondContractLength() > 500 && larryBondList.get(i).getBondContractLength() < 750 ) {
					twoYearMature2005 = twoYearMature2005 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 900 && larryBondList.get(i).getBondContractLength() < 1200) {
					threeYearMature2005 = threeYearMature2005 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 1500 && larryBondList.get(i).getBondContractLength() < 2000) {
					fiveYearMature2005 = fiveYearMature2005 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 2200 && larryBondList.get(i).getBondContractLength() < 3000) {
					sevenYearMature2005 = sevenYearMature2005 + larryBondList.get(i).getIssuedAmount();
				}
			}
			else if (larryBondList.get(i).getMaturityDate().getYear() == 2006) {
				if (larryBondList.get(i).getBondContractLength() > 500 && larryBondList.get(i).getBondContractLength() < 750 ) {
					twoYearMature2006 = twoYearMature2006 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 900 && larryBondList.get(i).getBondContractLength() < 1200) {
					threeYearMature2006 = threeYearMature2006 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 1500 && larryBondList.get(i).getBondContractLength() < 2000) {
					fiveYearMature2006 = fiveYearMature2006 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 2200 && larryBondList.get(i).getBondContractLength() < 3000) {
					sevenYearMature2006 = sevenYearMature2006 + larryBondList.get(i).getIssuedAmount();
				}
			}
			else if (larryBondList.get(i).getMaturityDate().getYear() == 2007) {
				if (larryBondList.get(i).getBondContractLength() > 500 && larryBondList.get(i).getBondContractLength() < 750 ) {
					twoYearMature2007 = twoYearMature2007 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 900 && larryBondList.get(i).getBondContractLength() < 1200) {
					threeYearMature2007 = threeYearMature2007 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 1500 && larryBondList.get(i).getBondContractLength() < 2000) {
					fiveYearMature2007 = fiveYearMature2007 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 2200 && larryBondList.get(i).getBondContractLength() < 3000) {
					sevenYearMature2007 = sevenYearMature2007 + larryBondList.get(i).getIssuedAmount();
				}
			}
			else if (larryBondList.get(i).getMaturityDate().getYear() == 2008) {
				if (larryBondList.get(i).getBondContractLength() > 500 && larryBondList.get(i).getBondContractLength() < 750 ) {
					twoYearMature2008 = twoYearMature2008 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 900 && larryBondList.get(i).getBondContractLength() < 1200) {
					threeYearMature2008 = threeYearMature2008 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 1500 && larryBondList.get(i).getBondContractLength() < 2000) {
					fiveYearMature2008 = fiveYearMature2008 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 2200 && larryBondList.get(i).getBondContractLength() < 3000) {
					sevenYearMature2008 = sevenYearMature2008 + larryBondList.get(i).getIssuedAmount();
				}
			}
			else if (larryBondList.get(i).getMaturityDate().getYear() == 2009) {
				if (larryBondList.get(i).getBondContractLength() > 500 && larryBondList.get(i).getBondContractLength() < 750 ) {
					twoYearMature2009 = twoYearMature2009 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 900 && larryBondList.get(i).getBondContractLength() < 1200) {
					threeYearMature2009 = threeYearMature2009 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 1500 && larryBondList.get(i).getBondContractLength() < 2000) {
					fiveYearMature2009 = fiveYearMature2009 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 2200 && larryBondList.get(i).getBondContractLength() < 3000) {
					sevenYearMature2009 = sevenYearMature2009 + larryBondList.get(i).getIssuedAmount();
				}
			}
			else if (larryBondList.get(i).getMaturityDate().getYear() == 2010) {
				if (larryBondList.get(i).getBondContractLength() > 500 && larryBondList.get(i).getBondContractLength() < 750 ) {
					twoYearMature2010 = twoYearMature2010 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 900 && larryBondList.get(i).getBondContractLength() < 1200) {
					threeYearMature2010 = threeYearMature2010 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 1500 && larryBondList.get(i).getBondContractLength() < 2000) {
					fiveYearMature2010 = fiveYearMature2010 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 2200 && larryBondList.get(i).getBondContractLength() < 3000) {
					sevenYearMature2010 = sevenYearMature2010 + larryBondList.get(i).getIssuedAmount();
				}
			}
			else if (larryBondList.get(i).getMaturityDate().getYear() == 2011) {
				if (larryBondList.get(i).getBondContractLength() > 500 && larryBondList.get(i).getBondContractLength() < 750 ) {
					twoYearMature2011 = twoYearMature2011 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 900 && larryBondList.get(i).getBondContractLength() < 1200) {
					threeYearMature2011 = threeYearMature2011 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 1500 && larryBondList.get(i).getBondContractLength() < 2000) {
					fiveYearMature2011 = fiveYearMature2011 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 2200 && larryBondList.get(i).getBondContractLength() < 3000) {
					sevenYearMature2011 = sevenYearMature2011 + larryBondList.get(i).getIssuedAmount();
				}
			}
			else if (larryBondList.get(i).getMaturityDate().getYear() == 2012) {
				if (larryBondList.get(i).getBondContractLength() > 500 && larryBondList.get(i).getBondContractLength() < 750 ) {
					twoYearMature2012 = twoYearMature2012 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 900 && larryBondList.get(i).getBondContractLength() < 1200) {
					threeYearMature2012 = threeYearMature2012 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 1500 && larryBondList.get(i).getBondContractLength() < 2000) {
					fiveYearMature2012 = fiveYearMature2012 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 2200 && larryBondList.get(i).getBondContractLength() < 3000) {
					sevenYearMature2012 = sevenYearMature2012 + larryBondList.get(i).getIssuedAmount();
				}
			}
			else if (larryBondList.get(i).getMaturityDate().getYear() == 2013) {
				if (larryBondList.get(i).getBondContractLength() > 500 && larryBondList.get(i).getBondContractLength() < 750 ) {
					twoYearMature2013 = twoYearMature2013 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 900 && larryBondList.get(i).getBondContractLength() < 1200) {
					threeYearMature2013 = threeYearMature2013 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 1500 && larryBondList.get(i).getBondContractLength() < 2000) {
					fiveYearMature2013 = fiveYearMature2013 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 2200 && larryBondList.get(i).getBondContractLength() < 3000) {
					sevenYearMature2013 = sevenYearMature2013 + larryBondList.get(i).getIssuedAmount();
				}
			}
			else if (larryBondList.get(i).getMaturityDate().getYear() == 2014) {
				if (larryBondList.get(i).getBondContractLength() > 500 && larryBondList.get(i).getBondContractLength() < 750 ) {
					twoYearMature2014 = twoYearMature2014 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 900 && larryBondList.get(i).getBondContractLength() < 1200) {
					threeYearMature2014 = threeYearMature2014 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 1500 && larryBondList.get(i).getBondContractLength() < 2000) {
					fiveYearMature2014 = fiveYearMature2014 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 2200 && larryBondList.get(i).getBondContractLength() < 3000) {
					sevenYearMature2014 = sevenYearMature2014 + larryBondList.get(i).getIssuedAmount();
				}
			}
			else if (larryBondList.get(i).getMaturityDate().getYear() == 2015) {
				if (larryBondList.get(i).getBondContractLength() > 500 && larryBondList.get(i).getBondContractLength() < 750 ) {
					twoYearMature2015 = twoYearMature2015 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 900 && larryBondList.get(i).getBondContractLength() < 1200) {
					threeYearMature2015 = threeYearMature2015 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 1500 && larryBondList.get(i).getBondContractLength() < 2000) {
					fiveYearMature2015 = fiveYearMature2015 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 2200 && larryBondList.get(i).getBondContractLength() < 3000) {
					sevenYearMature2015 = sevenYearMature2015 + larryBondList.get(i).getIssuedAmount();
				}
			}
			else if (larryBondList.get(i).getMaturityDate().getYear() == 2016) {
				if (larryBondList.get(i).getBondContractLength() > 500 && larryBondList.get(i).getBondContractLength() < 750 ) {
					twoYearMature2016 = twoYearMature2016 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 900 && larryBondList.get(i).getBondContractLength() < 1200) {
					threeYearMature2016 = threeYearMature2016 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 1500 && larryBondList.get(i).getBondContractLength() < 2000) {
					fiveYearMature2016 = fiveYearMature2016 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 2200 && larryBondList.get(i).getBondContractLength() < 3000) {
					sevenYearMature2016 = sevenYearMature2016 + larryBondList.get(i).getIssuedAmount();
				}
			}
			else if (larryBondList.get(i).getMaturityDate().getYear() == 2017) {
				if (larryBondList.get(i).getBondContractLength() > 500 && larryBondList.get(i).getBondContractLength() < 750 ) {
					twoYearMature2017 = twoYearMature2017 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 900 && larryBondList.get(i).getBondContractLength() < 1200) {
					threeYearMature2017 = threeYearMature2017 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 1500 && larryBondList.get(i).getBondContractLength() < 2000) {
					fiveYearMature2017 = fiveYearMature2017 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 2200 && larryBondList.get(i).getBondContractLength() < 3000) {
					sevenYearMature2017 = sevenYearMature2017 + larryBondList.get(i).getIssuedAmount();
				}
			}
			else if (larryBondList.get(i).getMaturityDate().getYear() == 2018) {
				if (larryBondList.get(i).getBondContractLength() > 500 && larryBondList.get(i).getBondContractLength() < 750 ) {
					twoYearMature2018 = twoYearMature2018 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 900 && larryBondList.get(i).getBondContractLength() < 1200) {
					threeYearMature2018 = threeYearMature2018 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 1500 && larryBondList.get(i).getBondContractLength() < 2000) {
					fiveYearMature2018 = fiveYearMature2018 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 2200 && larryBondList.get(i).getBondContractLength() < 3000) {
					sevenYearMature2018 = sevenYearMature2018 + larryBondList.get(i).getIssuedAmount();
				}
			}
			else if (larryBondList.get(i).getMaturityDate().getYear() == 2019) {
				if (larryBondList.get(i).getBondContractLength() > 500 && larryBondList.get(i).getBondContractLength() < 750 ) {
					twoYearMature2019 = twoYearMature2019 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 900 && larryBondList.get(i).getBondContractLength() < 1200) {
					threeYearMature2019 = threeYearMature2019 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 1500 && larryBondList.get(i).getBondContractLength() < 2000) {
					fiveYearMature2019 = fiveYearMature2019 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 2200 && larryBondList.get(i).getBondContractLength() < 3000) {
					sevenYearMature2019 = sevenYearMature2019 + larryBondList.get(i).getIssuedAmount();
				}
			}
			else if (larryBondList.get(i).getMaturityDate().getYear() == 2020) {
				if (larryBondList.get(i).getBondContractLength() > 500 && larryBondList.get(i).getBondContractLength() < 750 ) {
					twoYearMature2020 = twoYearMature2020 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 900 && larryBondList.get(i).getBondContractLength() < 1200) {
					threeYearMature2020 = threeYearMature2020 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 1500 && larryBondList.get(i).getBondContractLength() < 2000) {
					fiveYearMature2020 = fiveYearMature2020 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 2200 && larryBondList.get(i).getBondContractLength() < 3000) {
					sevenYearMature2020 = sevenYearMature2020 + larryBondList.get(i).getIssuedAmount();
				}
			}
			else if (larryBondList.get(i).getMaturityDate().getYear() == 2021) {
				if (larryBondList.get(i).getBondContractLength() > 500 && larryBondList.get(i).getBondContractLength() < 750 ) {
					twoYearMature2021 = twoYearMature2021 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 900 && larryBondList.get(i).getBondContractLength() < 1200) {
					threeYearMature2021 = threeYearMature2021 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 1500 && larryBondList.get(i).getBondContractLength() < 2000) {
					fiveYearMature2021 = fiveYearMature2021 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 2200 && larryBondList.get(i).getBondContractLength() < 3000) {
					sevenYearMature2021 = sevenYearMature2021 + larryBondList.get(i).getIssuedAmount();
				}
			}
			else if (larryBondList.get(i).getMaturityDate().getYear() == 2022) {
				if (larryBondList.get(i).getBondContractLength() > 500 && larryBondList.get(i).getBondContractLength() < 750 ) {
					twoYearMature2022 = twoYearMature2022 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 900 && larryBondList.get(i).getBondContractLength() < 1200) {
					threeYearMature2022 = threeYearMature2022 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 1500 && larryBondList.get(i).getBondContractLength() < 2000) {
					fiveYearMature2022 = fiveYearMature2022 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 2200 && larryBondList.get(i).getBondContractLength() < 3000) {
					sevenYearMature2022 = sevenYearMature2022 + larryBondList.get(i).getIssuedAmount();
				}
			}
			else if (larryBondList.get(i).getMaturityDate().getYear() == 2023) {
				if (larryBondList.get(i).getBondContractLength() > 500 && larryBondList.get(i).getBondContractLength() < 750 ) {
					twoYearMature2023 = twoYearMature2023 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 900 && larryBondList.get(i).getBondContractLength() < 1200) {
					threeYearMature2023 = threeYearMature2023 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 1500 && larryBondList.get(i).getBondContractLength() < 2000) {
					fiveYearMature2023 = fiveYearMature2023 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 2200 && larryBondList.get(i).getBondContractLength() < 3000) {
					sevenYearMature2023 = sevenYearMature2023 + larryBondList.get(i).getIssuedAmount();
				}
			}
			else if (larryBondList.get(i).getMaturityDate().getYear() == 2024) {
				if ( larryBondList.get(i).getBondContractLength() > 500 && larryBondList.get(i).getBondContractLength() < 750) {
					twoYearMature2024 = twoYearMature2024 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 900 && larryBondList.get(i).getBondContractLength() < 1200) {
					threeYearMature2024 = threeYearMature2024 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 1500 && larryBondList.get(i).getBondContractLength() < 2000) {
					fiveYearMature2024 = fiveYearMature2024 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 2200 && larryBondList.get(i).getBondContractLength() < 3000) {
					sevenYearMature2024 = sevenYearMature2024 + larryBondList.get(i).getIssuedAmount();
				}
			}
			else if (larryBondList.get(i).getMaturityDate().getYear() == 2025) {
				if ( larryBondList.get(i).getBondContractLength() > 500 && larryBondList.get(i).getBondContractLength() < 750) {
					twoYearMature2025 = twoYearMature2025 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 900 && larryBondList.get(i).getBondContractLength() < 1200) {
					threeYearMature2025 = threeYearMature2025 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 1500 && larryBondList.get(i).getBondContractLength() < 2000) {
					fiveYearMature2025 = fiveYearMature2025 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 2200 && larryBondList.get(i).getBondContractLength() < 3000) {
					sevenYearMature2025 = sevenYearMature2025 + larryBondList.get(i).getIssuedAmount();
				}
			}
			else if (larryBondList.get(i).getMaturityDate().getYear() == 2026) {
				if ( larryBondList.get(i).getBondContractLength() > 500 && larryBondList.get(i).getBondContractLength() < 750) {
					twoYearMature2026 = twoYearMature2026 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 900 && larryBondList.get(i).getBondContractLength() < 1200) {
					threeYearMature2026 = threeYearMature2026 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 1500 && larryBondList.get(i).getBondContractLength() < 2000) {
					fiveYearMature2026 = fiveYearMature2026 + larryBondList.get(i).getIssuedAmount();
				}
				else if ( larryBondList.get(i).getBondContractLength() > 2200 && larryBondList.get(i).getBondContractLength() < 3000) {
					sevenYearMature2026 = sevenYearMature2026 + larryBondList.get(i).getIssuedAmount();
				}
			}
		} 

		System.out.println("---- 2005 ----");
		System.out.println(twoYearMature2005);
		System.out.println(threeYearMature2005);
		System.out.println(fiveYearMature2005);
		System.out.println(sevenYearMature2005);
		System.out.println("-----");
		System.out.println("---- 2006 ----");
		System.out.println(twoYearMature2006);
		System.out.println(threeYearMature2006);
		System.out.println(fiveYearMature2006);
		System.out.println(sevenYearMature2006);
		System.out.println("-----");
		System.out.println("---- 2007 ----");
		System.out.println(twoYearMature2007);
		System.out.println(threeYearMature2007);
		System.out.println(fiveYearMature2007);
		System.out.println(sevenYearMature2007);
		System.out.println("-----");
		System.out.println("---- 2008 ----");
		System.out.println(twoYearMature2008);
		System.out.println(threeYearMature2008);
		System.out.println(fiveYearMature2008);
		System.out.println(sevenYearMature2008);
		System.out.println("-----");
		System.out.println("---- 2009 ----");
		System.out.println(twoYearMature2009);
		System.out.println(threeYearMature2009);
		System.out.println(fiveYearMature2009);
		System.out.println(sevenYearMature2009);
		System.out.println("-----");
		System.out.println("---- 2010 ----");
		System.out.println(twoYearMature2010);
		System.out.println(threeYearMature2010);
		System.out.println(fiveYearMature2010);
		System.out.println(sevenYearMature2010);
		System.out.println("-----");
		System.out.println("---- 2011 ----");
		System.out.println(twoYearMature2011);
		System.out.println(threeYearMature2011);
		System.out.println(fiveYearMature2011);
		System.out.println(sevenYearMature2011);
		System.out.println("-----");
		System.out.println("---- 2012 ----");
		System.out.println(twoYearMature2012);
		System.out.println(threeYearMature2012);
		System.out.println(fiveYearMature2012);
		System.out.println(sevenYearMature2012);
		System.out.println("-----");
		System.out.println("---- 2013 ----");
		System.out.println(twoYearMature2013);
		System.out.println(threeYearMature2013);
		System.out.println(fiveYearMature2013);
		System.out.println(sevenYearMature2013);
		System.out.println("-----");
		System.out.println("---- 2014 ----");
		System.out.println(twoYearMature2014);
		System.out.println(threeYearMature2014);
		System.out.println(fiveYearMature2014);
		System.out.println(sevenYearMature2014);
		System.out.println("-----");
		System.out.println("---- 2015 ----");
		System.out.println(twoYearMature2015);
		System.out.println(threeYearMature2015);
		System.out.println(fiveYearMature2015);
		System.out.println(sevenYearMature2015);
		System.out.println("-----");
		System.out.println("---- 2016 ----");
		System.out.println(twoYearMature2016);
		System.out.println(threeYearMature2016);
		System.out.println(fiveYearMature2016);
		System.out.println(sevenYearMature2016);
		System.out.println("-----");
		System.out.println("---- 2017 ----");
		System.out.println(twoYearMature2017);
		System.out.println(threeYearMature2017);
		System.out.println(fiveYearMature2017);
		System.out.println(sevenYearMature2017);
		System.out.println("-----");
		System.out.println("---- 2018 ----");
		System.out.println(twoYearMature2018);
		System.out.println(threeYearMature2018);
		System.out.println(fiveYearMature2018);
		System.out.println(sevenYearMature2018);
		System.out.println("-----");
		System.out.println("---- 2019 ----");
		System.out.println(twoYearMature2019);
		System.out.println(threeYearMature2019);
		System.out.println(fiveYearMature2019);
		System.out.println(sevenYearMature2019);
		System.out.println("-----");
		System.out.println("---- 2020 ----");
		System.out.println(twoYearMature2020);
		System.out.println(threeYearMature2020);
		System.out.println(fiveYearMature2020);
		System.out.println(sevenYearMature2020);
		System.out.println("-----");
		System.out.println("---- 2021 ----");
		System.out.println(twoYearMature2021);
		System.out.println(threeYearMature2021);
		System.out.println(fiveYearMature2021);
		System.out.println(sevenYearMature2021);
		System.out.println("-----");
		System.out.println("---- 2022 ----");
		System.out.println(twoYearMature2022);
		System.out.println(threeYearMature2022);
		System.out.println(fiveYearMature2022);
		System.out.println(sevenYearMature2022);
		System.out.println("-----");
		System.out.println("---- 2023 ----");
		System.out.println(twoYearMature2023);
		System.out.println(threeYearMature2023);
		System.out.println(fiveYearMature2023);
		System.out.println(sevenYearMature2023);
		System.out.println("-----");
		System.out.println("---- 2024 ----");
		System.out.println(twoYearMature2024);
		System.out.println(threeYearMature2024);
		System.out.println(fiveYearMature2024);
		System.out.println(sevenYearMature2024);
		System.out.println("-----");
		System.out.println("---- 2025 ----");
		System.out.println(twoYearMature2025);
		System.out.println(threeYearMature2025);
		System.out.println(fiveYearMature2025);
		System.out.println(sevenYearMature2025);
		System.out.println("-----");
		System.out.println("---- 2026 ----");
		System.out.println(twoYearMature2026);
		System.out.println(threeYearMature2026);
		System.out.println(fiveYearMature2026);
		System.out.println(sevenYearMature2026);
		/*

		System.out.println(compiler.totalDebtInOneYear(finalizedBonds));

	//	System.out.println(compiler.totalDebtInOneYear(finalizedBonds));

	//	System.out.printf("%10f%n", compiler.calculateTotalOutstandingInterestOneYear(finalizedBonds));
		Double[] testLengths = compiler.getDifferingBondLengths(finalizedBonds);

		Double[] percentageLengths = compiler.getTotalDebtPercentages(testLengths);

		compiler.calculateTotalInterestPaidUntil2050BaseAssumption(finalizedBonds); */

	}

	public void calculateTotalInterestPaidUntil2050BaseAssumption(ArrayList<BondData> bonds) {
		Double totalOutStandingDebt = calculateTotalOutstandingInterestOneYear(bonds);
		Double[] bondPercentageLengths = getTotalDebtPercentages(getDifferingBondLengths(bonds));
		Double gdpGrowth = 6.0;
		Double deficit = 6.0;
		Double oneYearInterestRate = 5.0;
		Double twoYearInterestRate = 5.0;
		Double threeYearInterestRate = 5.0;
		Double fiveYearInterestRate = 5.0;
		Double sevenYearInterestRate = 5.0;
		Double tenYearInterestRate = 5.0;
		Double twentyYearInterestRate = 5.0;
		Double thirtyYearInterestRate = 5.0;

		Double totalGDP = 26835000.0;
		for (int i = 2023; i < 2051; i++) {
			Double interestInCurrYear = calculateTotalOutstandingInterestOneYear(bonds);
			String formattedInterest = String.format("%.2f", interestInCurrYear);
			System.out.println("Interest Paymounts in Billions in the year: " + i + " is: " + formattedInterest);
		//	System.out.println(formattedInterest);
			for (int j = 0; j < bonds.size(); j++) {
				if (bonds.get(j).getMaturityDate().isBefore(LocalDate.of(i + 1, 1, 1))) {
					LocalDate issueDateOriginal = bonds.get(j).getIssuedDate();
					LocalDate maturityDateOriginal = bonds.get(j).getMaturityDate();
					Double contractLength = bonds.get(j).getBondContractLength();
					if (contractLength < 0) {
						contractLength = 30.0 * 365.0;
					}
					bonds.get(j).setIssuedDate(issueDateOriginal.plusDays(365));
					bonds.get(j).setMaturityDate(maturityDateOriginal.plusDays(contractLength.longValue()));
					if (contractLength <= 365 * 1) {
						bonds.get(j).setYield(oneYearInterestRate);
					}
					else if (contractLength <= 365 * 2) {
						bonds.get(j).setYield(twoYearInterestRate);
					}
					else if (contractLength <= 365 * 3) {
						bonds.get(j).setYield(threeYearInterestRate);
					}
					else if (contractLength <= 365 * 5) {
						bonds.get(j).setYield(fiveYearInterestRate);
					}
					else if (contractLength <= 365 * 7) {
						bonds.get(j).setYield(sevenYearInterestRate);
					}
					else if (contractLength <= 365 * 10) {
						bonds.get(j).setYield(tenYearInterestRate);
					}
					else if (contractLength <= 365 * 20) {
						bonds.get(j).setYield(twentyYearInterestRate);
					}
					else {
						bonds.get(j).setYield(thirtyYearInterestRate);
					}

				}
			}	
			// Issue More Debt. 
			Double totalDebtToReissue = totalGDP / 100 * deficit;	
			// Increase GDP.
			totalGDP = totalGDP * (1 + gdpGrowth/100);	

			

			BondData oneYearBond = new BondData("OneYear", LocalDate.of(i + 1, 1, 1), LocalDate.of(i + 2, 1, 1), 
												 totalDebtToReissue * bondPercentageLengths[0], oneYearInterestRate);
			BondData twoYearBond = new BondData("twoYear", LocalDate.of(i + 1, 1, 1), LocalDate.of(i + 3, 1, 1), 
												 totalDebtToReissue * bondPercentageLengths[1], twoYearInterestRate);
			BondData threeYearBond = new BondData("threeYear", LocalDate.of(i + 1, 1, 1), LocalDate.of(i + 4, 1, 1), 
												 totalDebtToReissue * bondPercentageLengths[2], threeYearInterestRate);
			BondData fiveYearBond = new BondData("fiveYear", LocalDate.of(i + 1, 1, 1), LocalDate.of(i + 6, 1, 1), 
												 totalDebtToReissue * bondPercentageLengths[4], fiveYearInterestRate);
			BondData sevenYearBond = new BondData("sevenYear", LocalDate.of(i + 1, 1, 1), LocalDate.of(i + 8, 1, 1), 
												 totalDebtToReissue * bondPercentageLengths[6], sevenYearInterestRate);
			BondData tenYearBond = new BondData("tenYear", LocalDate.of(i + 1, 1, 1), LocalDate.of(i + 11, 1, 1), 
												 totalDebtToReissue * bondPercentageLengths[9], tenYearInterestRate);
			BondData twentyYearBond = new BondData("twentyYear", LocalDate.of(i + 1, 1, 1), LocalDate.of(i + 21, 1, 1), 
												 totalDebtToReissue * bondPercentageLengths[19], twentyYearInterestRate);
			BondData thirtyYearBond = new BondData("thirtyYear", LocalDate.of(i + 1, 1, 1), LocalDate.of(i + 31, 1, 1), 
												 totalDebtToReissue * bondPercentageLengths[29], thirtyYearInterestRate);

			
			bonds.add(oneYearBond);
			bonds.add(twoYearBond);
			bonds.add(threeYearBond);
			bonds.add(fiveYearBond);
			bonds.add(sevenYearBond);
			bonds.add(tenYearBond);
			bonds.add(twentyYearBond);
			bonds.add(thirtyYearBond); 

		}
	}

	public Double calculateTotalOutstandingInterestOneYear(ArrayList<BondData> bonds) {
		Double totalInterest = 0.0;

		for (int i = 0; i < bonds.size(); i++) {
			System.out.println(bonds.get(i).getIssuedAmount() + "," + bonds.get(i).getYield());
			totalInterest = totalInterest + (bonds.get(i).getIssuedAmount() * bonds.get(i).getYield() / 100);
		}

		return totalInterest;
	}

	public Double totalDebtInOneYear(ArrayList<BondData> bonds) {
		Double totalDebt = 0.0;

		for (int i = 0; i < bonds.size(); i++) {
			totalDebt = totalDebt + bonds.get(i).getIssuedAmount();
		}

		return totalDebt;
	}

	//4,770,514.1807 
	//13,732,151.5407
	// 4,211,847.0565
	// 24,797,429.6292




	//issued : 1,121,566,460
	//outstanding: 1,125,550,419
	//New: 194,080,004
	public ArrayList<BondData> thinReissuedBonds(ArrayList<BondData> bonds) {
		ArrayList<BondData> tempHolder = new ArrayList<BondData>();

		String currentName = bonds.get(0).getBondIdentifier();

		tempHolder.add(new BondData(bonds.get(0).getBondIdentifier(), bonds.get(0).getIssuedDate(), bonds.get(0).getMaturityDate(), bonds.get(0).getIssuedAmount(), bonds.get(0).getYield()));
		for (int i = 0; i < bonds.size(); i++) {
			if (!currentName.equalsIgnoreCase(bonds.get(i).getBondIdentifier()) && bonds.get(i).getIssuedDate() != null && 
											  bonds.get(i).getYield() != null && bonds.get(i).getMaturityDate() != null && bonds.get(i).getIssuedAmount() != null) {
				Double yield = 0.0;
				if (bonds.get(i).getInterestRate() != null) {
					yield = bonds.get(i).getInterestRate();
				}
				else {
					yield = bonds.get(i).getYield();
				}
				tempHolder.add(new BondData(bonds.get(i).getBondIdentifier(), bonds.get(i).getIssuedDate(), bonds.get(i).getMaturityDate(), bonds.get(i).getIssuedAmount(), yield));
				currentName = bonds.get(i).getBondIdentifier();
			}
		}

		return tempHolder;
		
	}


	public ArrayList<BondData> deleteDuplicates(ArrayList<BondData> bonds) {
		Set<String> bondSet = new HashSet<String>();
		ArrayList<BondData> finalizedBonds = new ArrayList<BondData>();
		for (int i = 0; i < bonds.size(); i++) {
			if (!bondSet.contains(bonds.get(i).getDuplicateIdentifer()) && bonds.get(i).getYield() != null) {
				finalizedBonds.add(bonds.get(i));
				bondSet.add(bonds.get(i).getDuplicateIdentifer());
				
			}
		}

		return finalizedBonds;

	}

	public ArrayList<BondData> getOnlyBills(ArrayList<BondData> bonds) {
		ArrayList<BondData> bondOnly = new ArrayList<BondData>();

		for (int i = 0; i < bonds.size(); i++) {
			if (bonds.get(i).getSecurityClass().equalsIgnoreCase("Bills Maturity Value")) {
				bondOnly.add(bonds.get(i));
			}
		}

		return bondOnly;
 	}

 	public Double[] getTotalDebtPercentages(Double[] differingLengths) {
 		Double total = 0.0;
 		for (int i = 0; i < differingLengths.length; i++) {
 			if (differingLengths[i] != null) {
 				total = total + differingLengths[i];
 			}
 		}
 		Double[] bondLengthTotals = new Double[30];
 		bondLengthTotals[0] = differingLengths[0] / total;
		bondLengthTotals[1] = differingLengths[1] / total;
		bondLengthTotals[2] = differingLengths[2] / total;
		bondLengthTotals[4] = differingLengths[4] / total;
		bondLengthTotals[6] = differingLengths[6] / total;
		bondLengthTotals[9] = differingLengths[9] / total;
		bondLengthTotals[19] = differingLengths[19] / total;
		bondLengthTotals[29] = differingLengths[29] / total;

		return bondLengthTotals;
 	}

	//everything over 30 year, call 30 years for assumption of interest rate
	// Returns 1,2,3,5,7,10,20,30 TOTAL:
	public Double[] getDifferingBondLengths(ArrayList<BondData> bonds) {

		Double[] bondLengthTotals = new Double[30];

		Double numberOfOneYearBonds = 0.0;
		Double numberOfTwoYearBonds = 0.0;
		Double numberOfThreeYearBonds = 0.0;
		Double numberOfFiveYearBonds = 0.0;
		Double numberOfSevenYearBonds = 0.0;
		Double numberOfTenYearBonds = 0.0;
		Double numberOfTwentyYearBonds = 0.0;
		Double numberOfThirtyYearBonds = 0.0;
		Double numberOfLongerBonds = 0.0;
		Double numberOfNoData = 0.0;

		for (int i = 0; i < bonds.size(); i++) {
			if (bonds.get(i).getBondContractLength() == null) {
				numberOfNoData++;
			}
			else if (bonds.get(i).getBondContractLength() < 0) {
				numberOfThirtyYearBonds = numberOfThirtyYearBonds + bonds.get(i).getIssuedAmount();
			}
			else if (bonds.get(i).getBondContractLength() <= 365 * 1) {
				numberOfOneYearBonds = numberOfOneYearBonds + bonds.get(i).getIssuedAmount();
			}
			else if (bonds.get(i).getBondContractLength() <= 365 * 2) {
				numberOfTwoYearBonds = numberOfTwoYearBonds + bonds.get(i).getIssuedAmount();
			}
			else if (bonds.get(i).getBondContractLength() <= 365 * 3) {
				numberOfThreeYearBonds = numberOfThreeYearBonds + bonds.get(i).getIssuedAmount();
			}
			else if (bonds.get(i).getBondContractLength() <= 365 * 5) {
				numberOfFiveYearBonds = numberOfFiveYearBonds + bonds.get(i).getIssuedAmount();
			}
			else if (bonds.get(i).getBondContractLength() <= 365 * 7) {
				numberOfSevenYearBonds = numberOfSevenYearBonds + bonds.get(i).getIssuedAmount();
			}
			else if (bonds.get(i).getBondContractLength() <= 365 * 10) {
				numberOfTenYearBonds = numberOfTenYearBonds + bonds.get(i).getIssuedAmount();
			}
			else if (bonds.get(i).getBondContractLength() <= 365 * 20) {
				numberOfTwentyYearBonds = numberOfTwentyYearBonds + bonds.get(i).getIssuedAmount();
			}
			else {
				numberOfThirtyYearBonds = numberOfThirtyYearBonds + bonds.get(i).getIssuedAmount();
			}
		}

		bondLengthTotals[0] = numberOfOneYearBonds;
		bondLengthTotals[1] = numberOfTwoYearBonds;
		bondLengthTotals[2] = numberOfThreeYearBonds;
		bondLengthTotals[4] = numberOfFiveYearBonds;
		bondLengthTotals[6] = numberOfSevenYearBonds;
		bondLengthTotals[9] = numberOfTenYearBonds;
		bondLengthTotals[19] = numberOfTwentyYearBonds;
		bondLengthTotals[29] = numberOfThirtyYearBonds;

		return bondLengthTotals;
	}


	public ArrayList<BondData> parseFileHistory(String fileName) throws Exception {
		FileReader fileReader = new FileReader(fileName);

      	BufferedReader bufferedReader = new BufferedReader(fileReader);
		
		String line = null;

		ArrayList<BondData> bondData = new ArrayList<BondData>();


		bufferedReader.readLine(); // skips header

		while ( (line = bufferedReader.readLine()) != null ) {
			String[] parts = line.split(":");
			DateTimeFormatter inputFormatter = DateTimeFormatter.ofPattern("M/d/yy");
			DateTimeFormatter interestFormatter = DateTimeFormatter.ofPattern("d-MMM-yy", Locale.ENGLISH);

    		LocalDate recordDate = null;
    		if (parts[0] == null || parts[0].trim().isEmpty() || parts[0].trim().equalsIgnoreCase("null")) {
        		recordDate = null;
    		}
    		else if (parts[0].trim().equalsIgnoreCase("Feb-29")) {
    			recordDate = LocalDate.parse("29-Feb-23", interestFormatter);
    		}
    		else {
    			recordDate = LocalDate.parse(parts[0].trim(), inputFormatter);
    		}

    		LocalDate issuedDate = null;
    		if (parts[8] == null || parts[8].trim().isEmpty() || parts[8].trim().equalsIgnoreCase("null")) {
        		issuedDate = null;
    		}
    		else if (parts[8].trim().equalsIgnoreCase("Feb-29")) {
    			issuedDate = LocalDate.parse("29-Feb-23", interestFormatter);
    		}
    		else {
    			issuedDate = LocalDate.parse(parts[8].trim(), inputFormatter);
    		}

    		LocalDate maturityDate = null;
    		if (parts[9] == null || parts[9].trim().isEmpty() || parts[9].trim().equalsIgnoreCase("null")) {
        		maturityDate = null;
    		}
    		else if (parts[9].trim().equalsIgnoreCase("Feb-29")) {
    			maturityDate = LocalDate.parse("29-Feb-23", interestFormatter);
    		}
    		else {
    			maturityDate = LocalDate.parse(parts[9].trim(), inputFormatter);
    		}

    		LocalDate interestDate = null;
    		if (parts[10] == null || parts[10].trim().isEmpty() || parts[10].trim().equalsIgnoreCase("null")) {
        		interestDate = null;
    		}
    		else if (parts[10].trim().equalsIgnoreCase("Feb-29")) {
    			interestDate = LocalDate.parse("29-Feb-23", interestFormatter);
    		}
    		else {
    			interestDate = LocalDate.parse(parts[10].trim() + "-23", interestFormatter);
    		}
    		


    		Double interestRate = 0.0;
    		if (parts[6] == null || parts[6].trim().isEmpty() || parts[6].trim().equalsIgnoreCase("null")) {
        		interestRate = null;
    		}
    		else {
    			interestRate = Double.parseDouble(parts[6]);
    		}

    		Double yield = 0.0;
    		if (parts[7] == null || parts[7].trim().isEmpty() || parts[7].trim().equalsIgnoreCase("null")) {
        		yield = null;
    		}
    		else {
    			yield = Double.parseDouble(parts[7]);
    		}

    		Double issuedAmount = 0.0;
    		try {
            	issuedAmount = Double.parseDouble(parts[14].trim());
        	} 
        	catch (NumberFormatException e) {
            	issuedAmount = null;
        	}

    		Double amountAdjustedForInflation = 0.0;
    		try {
            	amountAdjustedForInflation = Double.parseDouble(parts[15].trim());
        	} 
        	catch (NumberFormatException e) {
            	amountAdjustedForInflation = null;
        	}

    		Double redeemedAmount = 0.0;
    		try {
            	redeemedAmount = Double.parseDouble(parts[16].trim());
        	} 
        	catch (NumberFormatException e) {
            	redeemedAmount = null;
        	}

    		Double outstandingAmount = 0.0;
    		try {
            	outstandingAmount = Double.parseDouble(parts[17].trim());
        	} 
        	catch (NumberFormatException e) {
            	outstandingAmount = null;
        	}

			BondData singleBond = new BondData(recordDate, parts[1].trim(), parts[3].trim(), parts[4].trim(), interestRate,  
											   yield, issuedDate, maturityDate,
											   interestDate, issuedAmount, amountAdjustedForInflation,
											   redeemedAmount, outstandingAmount);
			bondData.add(singleBond);


		}

		return bondData;
		
	}

	public ArrayList<BondData> parseFile(String fileName) throws Exception {
		FileReader fileReader = new FileReader(fileName);

      	BufferedReader bufferedReader = new BufferedReader(fileReader);
		
		String line = null;

		ArrayList<BondData> bondData = new ArrayList<BondData>();


		bufferedReader.readLine(); // skips header

		while ( (line = bufferedReader.readLine()) != null ) {
			String[] parts = line.split(",");
			DateTimeFormatter inputFormatter = DateTimeFormatter.ofPattern("yyyy-MM-dd");
			DateTimeFormatter interestFormatter = DateTimeFormatter.ofPattern("d-MMM-yy", Locale.ENGLISH);

    		LocalDate recordDate = null;
    		if (parts[0] == null || parts[0].trim().isEmpty() || parts[0].trim().equalsIgnoreCase("null")) {
        		recordDate = null;
    		}
    		else if (parts[0].trim().equalsIgnoreCase("Feb-29")) {
    			recordDate = LocalDate.parse("29-Feb-23", interestFormatter);
    		}
    		else {
    			recordDate = LocalDate.parse(parts[0].trim(), inputFormatter);
    		}

    		LocalDate issuedDate = null;
    		if (parts[8] == null || parts[8].trim().isEmpty() || parts[8].trim().equalsIgnoreCase("null")) {
        		issuedDate = null;
    		}
    		else if (parts[8].trim().equalsIgnoreCase("Feb-29")) {
    			issuedDate = LocalDate.parse("29-Feb-23", interestFormatter);
    		}
    		else {
    			issuedDate = LocalDate.parse(parts[8].trim(), inputFormatter);
    		}

    		LocalDate maturityDate = null;
    		if (parts[9] == null || parts[9].trim().isEmpty() || parts[9].trim().equalsIgnoreCase("null")) {
        		maturityDate = null;
    		}
    		else if (parts[9].trim().equalsIgnoreCase("Feb-29")) {
    			maturityDate = LocalDate.parse("29-Feb-23", interestFormatter);
    		}
    		else {
    			maturityDate = LocalDate.parse(parts[9].trim(), inputFormatter);
    		}

    		LocalDate interestDate = null;
    		/*
    		if (parts[10] == null || parts[10].trim().isEmpty() || parts[10].trim().equalsIgnoreCase("null")) {
        		interestDate = null;
    		}
    		else if (parts[10].trim().equalsIgnoreCase("Feb-29")) {
    			interestDate = LocalDate.parse("29-Feb-23", interestFormatter);
    		}
    		else {
    			interestDate = LocalDate.parse(parts[10].trim() + "-23", interestFormatter);
    		} */
    		


    		Double interestRate = 0.0;
    		if (parts[6] == null || parts[6].trim().isEmpty() || parts[6].trim().equalsIgnoreCase("null")) {
        		interestRate = null;
    		}
    		else {
    			interestRate = Double.parseDouble(parts[6]);
    		}

    		Double yield = 0.0;
    		if (parts[7] == null || parts[7].trim().isEmpty() || parts[7].trim().equalsIgnoreCase("null")) {
        		yield = null;
    		}
    		else {
    			yield = Double.parseDouble(parts[7]);
    		}

    		Double issuedAmount = 0.0;
    		try {
            	issuedAmount = Double.parseDouble(parts[14].trim());
        	} 
        	catch (NumberFormatException e) {
            	issuedAmount = null;
        	}

    		Double amountAdjustedForInflation = 0.0;
    		try {
            	amountAdjustedForInflation = Double.parseDouble(parts[15].trim());
        	} 
        	catch (NumberFormatException e) {
            	amountAdjustedForInflation = null;
        	}

    		Double redeemedAmount = 0.0;
    		try {
            	redeemedAmount = Double.parseDouble(parts[16].trim());
        	} 
        	catch (NumberFormatException e) {
            	redeemedAmount = null;
        	}

    		Double outstandingAmount = 0.0;
    		try {
            	outstandingAmount = Double.parseDouble(parts[17].trim());
        	} 
        	catch (NumberFormatException e) {
            	outstandingAmount = null;
        	}

			BondData singleBond = new BondData(recordDate, parts[1].trim(), parts[3].trim(), parts[4].trim(), interestRate,  
											   yield, issuedDate, maturityDate,
											   interestDate, issuedAmount, amountAdjustedForInflation,
											   redeemedAmount, outstandingAmount);
			bondData.add(singleBond);


		}

		return bondData;
		
	}



}
