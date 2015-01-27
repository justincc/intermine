package org.intermine.bio.dataconversion;

/*
 * Copyright (C) 2002-2015 FlyMine
 *
 * This code may be freely distributed and modified under the
 * terms of the GNU Lesser General Public Licence.  This should
 * be distributed with the code.  See the LICENSE file for more
 * information or http://www.gnu.org/copyleft/lesser.html.
 *
 */

import java.io.File;
import java.io.FileInputStream;
import java.io.Reader;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.apache.commons.lang.StringUtils;
import org.apache.log4j.Logger;
import org.biopax.paxtools.controller.PathAccessor;
import org.biopax.paxtools.io.BioPAXIOHandler;
import org.biopax.paxtools.io.jena.JenaIOHandler;
import org.biopax.paxtools.model.BioPAXLevel;
import org.biopax.paxtools.model.Model;
import org.biopax.paxtools.model.level3.Pathway;
import org.biopax.paxtools.model.level3.Xref;
import org.intermine.bio.util.OrganismData;
import org.intermine.bio.util.OrganismRepository;
import org.intermine.dataconversion.ItemWriter;
import org.intermine.objectstore.ObjectStoreException;
import org.intermine.xml.full.Item;
/**
 * Converts BioPAX files into InterMine objects.
 *
 * @author Julie Sullivan
 */
public class BioPAXConverter extends BioFileConverter
{
    private static final Logger LOG = Logger.getLogger(BioPAXConverter.class);
    private String organismRefId = null;
    private Set<String> taxonIds = new HashSet<String>();
    private OrganismRepository or;
    private Map<String, Item> pathways = new HashMap<String, Item>();
    private Map<String, String> proteins = new HashMap<String, String>();

    /**
     * Constructor
     * @param writer the ItemWriter used to handle the resultant items
     * @param intermineModel the Model
     * @throws ObjectStoreException if something goes horribly wrong
     */
    @SuppressWarnings("unchecked")
    public BioPAXConverter(ItemWriter writer, org.intermine.metadata.Model intermineModel)
        throws ObjectStoreException {
        super(writer, intermineModel);
        or = OrganismRepository.getOrganismRepository();
    }

    /**
     * {@inheritDoc}
     */
    @Override
    public void process(Reader reader) throws Exception {
        String taxonId = getTaxonId();
        if (taxonId == null) {
            // this file isn't from an organism specified in the project file
            return;
        }
        organismRefId = getOrganism(taxonId);

        // navigate through the owl file
        BioPAXIOHandler handler = new JenaIOHandler(BioPAXLevel.L3);
        Model model = handler.convertFromOWL(new FileInputStream(getCurrentFile()));

        for (Pathway pathway : model.getObjects(Pathway.class)) {
            PathAccessor pathAccessor = new PathAccessor(
                    "Pathway/pathwayComponent*/participant*:Protein/entityReference");

            String pathwayName = pathway.getDisplayName();
            Item pathwayItem = getPathway(pathwayName);
            Set<Xref> unificationXrefs = pathAccessor.getValueFromBean(pathway);
            for (Xref xref : unificationXrefs) {
                String accession = xref.getId();
                String refId = proteins.get(accession);
                if (refId == null) {
                    Item item = createItem("Protein");
                    item.setAttribute("primaryAccession", accession);
                    item.setReference("organism", organismRefId);
                    store(item);
                    refId = item.getIdentifier();
                    proteins.put(accession, refId);
                    pathwayItem.addToCollection("proteins", item);
                }
            }
        }
    }

    private Item getPathway(String pathwayName) throws ObjectStoreException {
        Item item = pathways.get(pathwayName);
        if (item == null) {
            item = createItem("Pathway");
            item.setAttribute("name", pathwayName);
            store(item);
            pathways.put(pathwayName, item);
        }
        return item;
    }


    /**
     * Sets the list of taxonIds that should be imported if using split input files.
     *
     * @param taxonIds a space-separated list of taxonIds
     */
    public void setBiopaxOrganisms(String taxonIds) {
        this.taxonIds = new HashSet<String>(Arrays.asList(StringUtils.split(taxonIds, " ")));
        LOG.info("Setting list of organisms to " + this.taxonIds);
    }


    /**
     * Use the file name currently being processed to divine the name of the organism.  Return null
     * if this taxonId is not in our list of taxonIds to be processed.
     * @return the taxonId of current organism
     */
    private String getTaxonId() {

        int taxonId;

        File file = getCurrentFile();
        String filename = file.getName();

        Pattern taxonIdPattern = Pattern.compile("^\\d+$");
        Matcher m = taxonIdPattern.matcher(filename.split("\\.")[0]);
        OrganismData od;

        if (m.find()) {
            // Good file name: 83333.owl
            taxonId = Integer.valueOf(filename.split("\\.")[0]);
        } else {
            // underscore or space
            String[] bits = filename.split("[_\\s]");

            // bad filename eg `Human immunodeficiency virus 1.owl`,
            // expecting "Drosophila melanogaster.owl"
            if (bits.length != 2) {
                String msg = "Bad filename:  '" + filename + "'.  Expecting filename in the format "
                    + "'Drosophila melanogaster.owl'";
                LOG.error(msg);
                return null;
            }

            String genus = bits[0];
            String species = bits[1].split("\\.")[0];
            String organismName = genus + " " + species;

            // Caution: organism.xml data should be read in/integrated to data first
            od = or.getOrganismDataByGenusSpecies(genus, species);
            if (od == null) {
                LOG.error("No data for " + organismName + ".  Please add to repository.");
                return null;
            }

            taxonId = od.getTaxonId();
        }

        String taxonIdString = String.valueOf(taxonId);

        // only process the taxonids set in the project XML file - if any
        if (!taxonIds.isEmpty() && !taxonIds.contains(taxonIdString)) {
            return null;
        }
        return taxonIdString;
    }

    /**
     * {@inheritDoc}
     */
    @Override
    public void close()
        throws ObjectStoreException {
        for (Item item : pathways.values()) {
            store(item);
        }
    }

    /**
     * Class to hold the config info for each taxonId.
     */
    class Config
    {
        protected String bioentity;
        protected String identifier;
        protected String db;

        /**
         * Constructor.
         */
        Config() {
            // nothing to do
        }

        /**
         * @return the bioentity
         */
        public String getBioentity() {
            return bioentity;
        }

        /**
         * @param bioentity the bioentity to set
         */
        public void setBioentity(String bioentity) {
            this.bioentity = bioentity;
        }

        /**
         * @return the identifier
         */
        public String getIdentifier() {
            return identifier;
        }

        /**
         * @param identifier the identifier to set
         */
        public void setIdentifier(String identifier) {
            this.identifier = identifier;
        }

        /**
         * @return the db
         */
        public String getDb() {
            return db;
        }

        /**
         * @param db the db to set
         */
        public void setDb(String db) {
            this.db = db;
        }
    }
}
