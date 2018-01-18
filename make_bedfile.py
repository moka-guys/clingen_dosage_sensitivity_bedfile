import urllib 
from datetime import datetime

class colourful_bedfiles():
    def __init__(self):
        # ftp link for the haploinsufficiency bed file
        self.haplo_link="ftp://ftp.ncbi.nlm.nih.gov/pub/dbVar/clingen/ClinGen_haploinsufficiency_gene.bed"
        # ftp link for the triplosensitivity bed file
        self.triplo_link="ftp://ftp.ncbi.nlm.nih.gov/pub/dbVar/clingen/ClinGen_triplosensitivity_gene.bed"
        # header for the bed file, using a placeholder for the track name
        self.header="track name=%s type=bedDetail db=hg19 visibility=3 itemRgb=On\n"
        # create a timestamp
        self.now=datetime.now()
        # format the timestamp
        self.now=datetime.strftime(self.now, "%Y%m%d")
        # folder to output the new bedfiles
        self.output_folder="/home/aled/Documents/171211_haplo_triplo_bedfile/"
        # name of the haplosensitivity track file
        self.haplo_outfile=self.output_folder+self.now+"haplo.bed"
        # name of the triplosensitivity track file
        self.triplo_outfile=self.output_folder+self.now+"triplo.bed"
        # dict to set the shade (score field) for the level of sensitivity 
        self.redcolour_dict={"1":"255,153,153","2":"255,102,102","3":"255,0,0"}
        self.bluecolour_dict={"1":"153,204,255","2":"102,178,255","3":"0,0,255"}
    
    def return_FTP(self,url):
        """
        function which recieves a url and returns the result
        The result is a list where the first element in the list is a temporary file containing what was returned from the url
        """
        # return the result from the ftp link passed to the function
        return urllib.urlretrieve(url)

    def go(self):
        """
        this function takes the ftp links, and passes the links to the return_FTP function which saves the file to temp folder
        this temporary file is returned and this can be used to read the file into a list
        When lists are populated for the haploinsufficency and triplosensitivity bed files the data is reformatted into a bedDetail format
        This creates bed files which can be used as tracks in genome browsers where regions are colour coded based on the evidence
        """
        # capture the file path of the temp folder containing the haploinsufficiency data 
        haplo_file_path=self.return_FTP(self.haplo_link)[0]
        # open this temp file and read into a list
        with open(haplo_file_path,'r') as haplo_file:
            haplo_file_list=haplo_file.readlines()
        
        # urllib has a bug where multiple files can't be downloaded - need to clean cache before downloading the next file
        urllib.urlcleanup()

        # capture the file path of the temp folder containing the triplosensitivity data 
        triplo_file_path=self.return_FTP(self.triplo_link)[0]
        # open this temp file and read into a list
        with open(triplo_file_path,'r') as triplo_file:
            triplo_file_list=triplo_file.readlines()

        # open the output file for triplosensitivity bedfile
        with open(self.triplo_outfile,'w') as triplo_bed_detail:
            # write the header, passing the trackname and timestamp
            triplo_bed_detail.write(self.header % ("ClingenTriplosensitivity"+self.now))
            # for line in the temp file list
            for line in triplo_file_list:
                # if it isn't the header
                if line.startswith("chr"):
                    # split the line on tab
                    splitline=line.split("\t")
                    # the downloaded bedfile is 5 columns, chr, start,stop, genesymbol and then a score for the level to which that region is triplosensitive
                    # define the name of each column
                    chrom=splitline[0]
                    start=splitline[1]
                    stop=splitline[2]
                    symbol=splitline[3]
                    score=splitline[4].rstrip() # remove new line characters
                    
                    # for each region need to create some extra columns to define the colour of the region
                    # if the score is not yet evaluated pass
                    if score == "Not yet evaluated":
                        pass
                    else:
                        # if the score is 1 2 or 3 it requires a blue colour with increasing levels of transparancy to denote strength of evidence
                        # the itemRGB defines the colour
                        # shade defines the level of transparacncy
                        # this uses the values defined in self.colour_dict
                        if score in self.bluecolour_dict:
                            itemRGB = self.bluecolour_dict[score]
                        # if the score == 30 then it is a autosomal recessive condition and should be grey
                        elif score == "30":
                            itemRGB = "128,128,128"
                        # if the score = 0 there is no evidence so should be yellow
                        elif score == "0":
                            itemRGB="255,250,205"
                        # if the score is not captured above print
                        else:
                            print "unknown score for line:"
                            print line
                        # set shade = 900 to denote the transparancy of the colour
                        shade = "900"
                        # define the strand as '.' to denote unknown
                        strand="."
                        # write this line to file in form
                        # chrom start stop symbol shade strand start stop itemRGB symbol symbol (as per https://genome.ucsc.edu/FAQ/FAQformat.html#format1.7)
                        # the last two columns of the bed detail format denote an ID and a description, currently this is the gene symbol in each field
                        triplo_bed_detail.write("\t".join([chrom,start,stop,symbol+" ("+score+")",shade,strand,start,stop,itemRGB,symbol+" ("+score+")",symbol+" ("+score+")\n"]))

        # repeat for haploinsufficiency file
        # open the output file for triplosensitivity bedfile
        with open(self.haplo_outfile,'w') as haplo_bed_detail:
            # write the header, passing the trackname and timestamp
            haplo_bed_detail.write(self.header % ("ClingenHaploInsufficiency"+self.now))
            
            # # for testing the colours chosen
            # for i in self.redcolour_dict:
            #     haplo_bed_detail.write("chr1	100652477	100652480	DBT	900	.	100652477	100652480	%s	DBT	DBT\n" % (self.redcolour_dict[i]))
            # for j in self.bluecolour_dict:
            #     haplo_bed_detail.write("chr1	100652477	100652480	DBT	900	.	100652477	100652480	%s	DBT	DBT\n" % (self.bluecolour_dict[j]))
            
            # for line in the temp file list
            for line in haplo_file_list:
                # if it isn't the header
                if line.startswith("chr"):
                    # split the line on tab
                    splitline=line.split("\t")
                    # the downloaded bedfile is 5 columns, chr, start,stop, genesymbol and then a score for the level to which that region is haploinsufficient
                    # define the name of each column
                    chrom=splitline[0]
                    start=splitline[1]
                    stop=splitline[2]
                    symbol=splitline[3]
                    score=splitline[4].rstrip() # remove new line characters
                    
                    # for each region need to create some extra columns to define the colour of the region
                    # if the score is not yet evaluated pass
                    if score == "Not yet evaluated":
                        pass
                    else:
                        # if the score is 1 2 or 3 it requires a red colour with increasing levels of transparancy to denote strength of evidence
                        # the itemRGB defines the colour
                        # shade defines the level of transparacncy
                        # this uses the values defined in self.colour_dict
                        if score in self.redcolour_dict:
                            itemRGB = self.redcolour_dict[score]
                        # if the score == 30 then it is a autosomal recessive condition and should be grey
                        elif score == "30":
                            itemRGB = "128,128,128"
                        # if the score = 0 there is no evidence so should be yellow
                        elif score == "0":
                            itemRGB="255,250,205"
                        # if the score is not captured above print
                        else:
                            print "unknown score for line:"
                            print line
                        # set shade = 900 to denote the transparancy of the colour
                        shade = "900"
                        # define the strand as '.' to denote unknown
                        strand="."
                        # write this line to file in form
                        # chrom start stop symbol shade strand start stop itemRGB symbol symbol (as per https://genome.ucsc.edu/FAQ/FAQformat.html#format1.7)
                        # the last two columns of the bed detail format denote an ID and a description, currently this is the gene symbol in each field
                        haplo_bed_detail.write("\t".join([chrom,start,stop,symbol+" ("+score+")",shade,strand,start,stop,itemRGB,symbol+" ("+score+")",symbol+" ("+score+")\n"]))



def main():
    go=colourful_bedfiles()
    go.go()

if __name__=="__main__":
    main()